from django.contrib import admin

from .models import Pelicula


@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "anio", "director", "genero", "estado", "puntuacion")
    list_filter = ("estado", "genero", "anio")
    search_fields = ("titulo", "director", "sinopsis")
    ordering = ("-creada_en", "titulo")
