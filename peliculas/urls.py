from django.urls import path

from . import views

app_name = "peliculas"

urlpatterns = [
    path("", views.lista_peliculas, name="lista"),
    path("nueva/", views.crear_pelicula, name="crear"),
    path("<int:pk>/", views.detalle_pelicula, name="detalle"),
    path("<int:pk>/editar/", views.editar_pelicula, name="editar"),
    path("<int:pk>/eliminar/", views.eliminar_pelicula, name="eliminar"),
]
