from django.contrib import admin

from .models import Categoria, MovimientoStock, Producto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "nombre",
        "categoria",
        "precio",
        "stock",
        "stock_minimo",
        "fecha_creacion",
    )
    search_fields = ("nombre", "descripcion", "categoria__nombre")
    list_filter = ("categoria", "fecha_creacion")


@admin.register(MovimientoStock)
class MovimientoStockAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_producto",
        "tipo",
        "cantidad",
        "stock_anterior",
        "stock_nuevo",
        "creado_en",
    )
    search_fields = ("nombre_producto", "notas")
    list_filter = ("tipo", "creado_en")
    readonly_fields = (
        "producto",
        "nombre_producto",
        "tipo",
        "cantidad",
        "stock_anterior",
        "stock_nuevo",
        "notas",
        "creado_en",
    )
