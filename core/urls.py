from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.lista_productos, name="lista_productos"),
    path("exportar/", views.exportar_productos, name="exportar_productos"),
    path(
        "<int:pk>/movimientos/",
        views.movimientos_producto,
        name="movimientos_producto",
    ),
    path("crear/", views.crear_producto, name="crear_producto"),
    path("editar/<int:pk>/", views.editar_producto, name="editar_producto"),
    path("eliminar/<int:pk>/", views.eliminar_producto, name="eliminar_producto"),
    path("categorias/", views.lista_categorias, name="lista_categorias"),
    path("categorias/crear/", views.crear_categoria, name="crear_categoria"),
    path(
        "categorias/<int:pk>/eliminar/",
        views.eliminar_categoria,
        name="eliminar_categoria",
    ),
]
