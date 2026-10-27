from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PeliculaForm
from .models import Pelicula


def lista_peliculas(request):
    peliculas = Pelicula.objects.all()
    busqueda = request.GET.get("q", "").strip()
    genero = request.GET.get("genero", "")
    estado = request.GET.get("estado", "")
    orden = request.GET.get("orden", "recientes")

    if busqueda:
        peliculas = peliculas.filter(
            Q(titulo__icontains=busqueda)
            | Q(director__icontains=busqueda)
            | Q(sinopsis__icontains=busqueda)
        )
    if genero in Pelicula.Genero.values:
        peliculas = peliculas.filter(genero=genero)
    if estado in Pelicula.Estado.values:
        peliculas = peliculas.filter(estado=estado)

    ordenes = {
        "recientes": ("-creada_en", "titulo"),
        "titulo": ("titulo", "anio"),
        "anio": ("-anio", "titulo"),
        "puntuacion": ("-puntuacion", "titulo"),
    }
    peliculas = peliculas.order_by(*ordenes.get(orden, ordenes["recientes"]))
    pagina = Paginator(peliculas, 12).get_page(request.GET.get("page"))

    contexto = {
        "peliculas": pagina,
        "pagina": pagina,
        "busqueda": busqueda,
        "genero_seleccionado": genero,
        "estado_seleccionado": estado,
        "orden_seleccionado": orden,
        "generos": Pelicula.Genero.choices,
        "estados": Pelicula.Estado.choices,
        "total_peliculas": Pelicula.objects.count(),
        "pendientes": Pelicula.objects.filter(estado=Pelicula.Estado.PENDIENTE).count(),
        "vistas": Pelicula.objects.filter(estado=Pelicula.Estado.VISTA).count(),
        "promedio": Pelicula.objects.filter(puntuacion__isnull=False).aggregate(
            promedio=Avg("puntuacion")
        )["promedio"],
    }
    return render(request, "peliculas/lista.html", contexto)


def detalle_pelicula(request, pk):
    pelicula = get_object_or_404(Pelicula, pk=pk)
    return render(request, "peliculas/detalle.html", {"pelicula": pelicula})


def crear_pelicula(request):
    form = PeliculaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        pelicula = form.save()
        messages.success(request, f'"{pelicula.titulo}" se agregó a tu colección.')
        return redirect("peliculas:detalle", pk=pelicula.pk)
    return render(
        request,
        "peliculas/formulario.html",
        {"form": form, "titulo": "Agregar película"},
    )


def editar_pelicula(request, pk):
    pelicula = get_object_or_404(Pelicula, pk=pk)
    form = PeliculaForm(request.POST or None, instance=pelicula)
    if request.method == "POST" and form.is_valid():
        pelicula = form.save()
        messages.success(request, "Los datos de la película se actualizaron.")
        return redirect("peliculas:detalle", pk=pelicula.pk)
    return render(
        request,
        "peliculas/formulario.html",
        {"form": form, "titulo": "Editar película", "pelicula": pelicula},
    )


def eliminar_pelicula(request, pk):
    pelicula = get_object_or_404(Pelicula, pk=pk)
    if request.method == "POST":
        titulo = pelicula.titulo
        pelicula.delete()
        messages.success(request, f'"{titulo}" se eliminó de tu colección.')
        return redirect("peliculas:lista")
    return render(
        request,
        "peliculas/confirmar_eliminacion.html",
        {"pelicula": pelicula},
    )
