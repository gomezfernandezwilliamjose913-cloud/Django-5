import csv
from decimal import Decimal

from django.core.paginator import Paginator
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.db import transaction
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CategoriaForm, MovimientoStockForm, ProductoForm
from .models import Categoria, MovimientoStock, Producto


ORDENES_PRODUCTOS = {
    "nombre": "nombre",
    "precio": "precio",
    "stock": "stock",
    "categoria": "categoria__nombre",
    "recientes": "-fecha_creacion",
}


def productos_filtrados(request):
    productos = Producto.objects.select_related("categoria").order_by("nombre")
    busqueda = request.GET.get("q", "").strip()
    categoria_id = request.GET.get("categoria", "")
    estado_stock = request.GET.get("stock", "")
    orden = request.GET.get("orden", "nombre")

    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda)
            | Q(descripcion__icontains=busqueda)
            | Q(categoria__nombre__icontains=busqueda)
        )
    if categoria_id.isdigit():
        productos = productos.filter(categoria_id=int(categoria_id))
    if estado_stock == "bajo":
        productos = productos.filter(stock__lte=F("stock_minimo"))
    elif estado_stock == "disponible":
        productos = productos.filter(stock__gt=F("stock_minimo"))

    campo_orden = ORDENES_PRODUCTOS.get(orden, "nombre")
    return (
        productos.order_by(campo_orden, "nombre"),
        busqueda,
        categoria_id,
        estado_stock,
        orden,
    )


def lista_productos(request):
    productos, busqueda, categoria_id, estado_stock, orden = productos_filtrados(
        request
    )
    paginador = Paginator(productos, 10)
    pagina = paginador.get_page(request.GET.get("page"))
    contexto = {
        "productos": pagina,
        "pagina": pagina,
        "categorias": Categoria.objects.all(),
        "busqueda": busqueda,
        "categoria_seleccionada": categoria_id,
        "estado_stock": estado_stock,
        "total_productos": Producto.objects.count(),
        "total_unidades": Producto.objects.aggregate(total=Coalesce(Sum("stock"), 0))[
            "total"
        ],
        "productos_stock_bajo": Producto.objects.filter(
            stock__lte=F("stock_minimo")
        ).count(),
        "valor_inventario": Producto.objects.aggregate(
            total=Coalesce(
                Sum(F("precio") * F("stock")),
                Decimal("0.00"),
            )
        )["total"],
        "categorias_activas": Categoria.objects.annotate(
            cantidad=Count("productos")
        ).filter(cantidad__gt=0).count(),
        "orden_seleccionado": orden,
    }
    return render(request, "core/lista.html", contexto)


def exportar_productos(request):
    productos, _, _, _, _ = productos_filtrados(request)
    respuesta = HttpResponse(content_type="text/csv; charset=utf-8")
    respuesta["Content-Disposition"] = 'attachment; filename="inventario.csv"'
    respuesta.write("\ufeff")
    escritor = csv.writer(respuesta)
    escritor.writerow(
        [
            "Producto",
            "Categoría",
            "Descripción",
            "Precio",
            "Stock",
            "Stock mínimo",
        ]
    )
    for producto in productos:
        escritor.writerow(
            [
                producto.nombre,
                producto.categoria.nombre if producto.categoria else "",
                producto.descripcion,
                producto.precio,
                producto.stock,
                producto.stock_minimo,
            ]
        )
    return respuesta


def crear_producto(request):
    form = ProductoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            producto = form.save()
            if producto.stock:
                MovimientoStock.objects.create(
                    producto=producto,
                    nombre_producto=producto.nombre,
                    tipo=MovimientoStock.Tipo.ENTRADA,
                    cantidad=producto.stock,
                    stock_anterior=0,
                    stock_nuevo=producto.stock,
                    notas="Existencia inicial",
                )
        messages.success(request, "El producto se creó correctamente.")
        return redirect("core:lista_productos")
    return render(
        request,
        "core/formulario.html",
        {"form": form, "titulo": "Nuevo producto"},
    )


def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    stock_anterior = producto.stock
    form = ProductoForm(request.POST or None, instance=producto)
    if request.method == "POST" and form.is_valid():
        stock_nuevo = form.cleaned_data["stock"]
        with transaction.atomic():
            producto = form.save()
            if stock_nuevo != stock_anterior:
                MovimientoStock.objects.create(
                    producto=producto,
                    nombre_producto=producto.nombre,
                    tipo=MovimientoStock.Tipo.AJUSTE,
                    cantidad=abs(stock_nuevo - stock_anterior),
                    stock_anterior=stock_anterior,
                    stock_nuevo=stock_nuevo,
                    notas="Ajuste desde el formulario del producto",
                )
        messages.success(request, "Los cambios del producto se guardaron.")
        return redirect("core:lista_productos")
    return render(
        request,
        "core/formulario.html",
        {"form": form, "titulo": "Editar producto"},
    )


def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == "POST":
        producto.delete()
        messages.success(request, "El producto se eliminó del inventario.")
        return redirect("core:lista_productos")
    return render(
        request,
        "core/confirmar_eliminacion.html",
        {"producto": producto},
    )


def lista_categorias(request):
    categorias = Categoria.objects.annotate(cantidad=Count("productos"))
    form = CategoriaForm()
    return render(
        request,
        "core/categorias.html",
        {"categorias": categorias, "form": form},
    )


def crear_categoria(request):
    if request.method == "POST":
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "La categoría se creó correctamente.")
            return redirect("core:lista_categorias")
        categorias = Categoria.objects.annotate(cantidad=Count("productos"))
        return render(
            request,
            "core/categorias.html",
            {"categorias": categorias, "form": form},
        )
    return redirect("core:lista_categorias")


def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == "POST":
        categoria.delete()
        messages.success(request, "La categoría se eliminó correctamente.")
    return redirect("core:lista_categorias")


def movimientos_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    form = MovimientoStockForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            producto = Producto.objects.select_for_update().get(pk=pk)
            movimiento = form.save(commit=False)
            stock_anterior = producto.stock
            if movimiento.tipo == MovimientoStock.Tipo.SALIDA:
                if movimiento.cantidad > stock_anterior:
                    form.add_error(
                        "cantidad",
                        f"No puedes retirar {movimiento.cantidad} unidades; "
                        f"solo hay {stock_anterior} disponibles.",
                    )
                else:
                    producto.stock -= movimiento.cantidad
            else:
                producto.stock += movimiento.cantidad

            if form.errors:
                movimientos = producto.movimientos.all()
                return render(
                    request,
                    "core/movimientos.html",
                    {"producto": producto, "movimientos": movimientos, "form": form},
                )

            producto.save(update_fields=["stock"])
            movimiento.producto = producto
            movimiento.nombre_producto = producto.nombre
            movimiento.stock_anterior = stock_anterior
            movimiento.stock_nuevo = producto.stock
            movimiento.save()
        messages.success(request, "El movimiento de inventario quedó registrado.")
        return redirect("core:movimientos_producto", pk=pk)

    return render(
        request,
        "core/movimientos.html",
        {
            "producto": producto,
            "movimientos": producto.movimientos.all(),
            "form": form,
        },
    )
