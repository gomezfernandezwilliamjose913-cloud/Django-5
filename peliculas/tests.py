from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Pelicula


class GestionPeliculasTests(TestCase):
    def setUp(self):
        self.pelicula = Pelicula.objects.create(
            titulo="La llegada",
            director="Denis Villeneuve",
            genero=Pelicula.Genero.CIENCIA_FICCION,
            anio=2016,
            duracion=116,
            puntuacion="8.2",
            estado=Pelicula.Estado.VISTA,
        )
        self.otra_pelicula = Pelicula.objects.create(
            titulo="Paddington",
            genero=Pelicula.Genero.COMEDIA,
            anio=2014,
            estado=Pelicula.Estado.PENDIENTE,
        )

    def test_panel_muestra_coleccion_y_resumen(self):
        response = self.client.get(reverse("peliculas:lista"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_peliculas"], 2)
        self.assertEqual(response.context["pendientes"], 1)
        self.assertEqual(response.context["vistas"], 1)
        self.assertEqual(response.context["promedio"], Decimal("8.2"))
        self.assertContains(response, "La llegada")
        self.assertContains(response, "Paddington")

    def test_busqueda_por_director_y_filtros(self):
        response = self.client.get(
            reverse("peliculas:lista"),
            {"q": "Villeneuve", "genero": "ciencia_ficcion", "estado": "vista"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["peliculas"]), [self.pelicula])

    def test_crear_pelicula(self):
        response = self.client.post(
            reverse("peliculas:crear"),
            {
                "titulo": "Coco",
                "director": "Lee Unkrich",
                "genero": "animacion",
                "anio": "2017",
                "duracion": "105",
                "puntuacion": "9.0",
                "estado": "pendiente",
                "imagen_url": "",
                "sinopsis": "Una aventura musical.",
            },
        )

        pelicula = Pelicula.objects.get(titulo="Coco")
        self.assertRedirects(
            response,
            reverse("peliculas:detalle", args=[pelicula.pk]),
        )
        self.assertEqual(pelicula.director, "Lee Unkrich")

    def test_puntuacion_fuera_de_rango_no_se_guarda(self):
        response = self.client.post(
            reverse("peliculas:crear"),
            {
                "titulo": "Película inválida",
                "director": "",
                "genero": "otro",
                "anio": "2020",
                "duracion": "",
                "puntuacion": "11",
                "estado": "pendiente",
                "imagen_url": "",
                "sinopsis": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Pelicula.objects.filter(titulo="Película inválida").exists())
        self.assertTrue(response.context["form"].errors["puntuacion"])

    def test_editar_pelicula(self):
        response = self.client.post(
            reverse("peliculas:editar", args=[self.pelicula.pk]),
            {
                "titulo": "La llegada",
                "director": "Denis Villeneuve",
                "genero": "ciencia_ficcion",
                "anio": "2016",
                "duracion": "116",
                "puntuacion": "9.0",
                "estado": "vista",
                "imagen_url": "",
                "sinopsis": "Una nueva sinopsis.",
            },
        )

        self.assertRedirects(
            response,
            reverse("peliculas:detalle", args=[self.pelicula.pk]),
        )
        self.pelicula.refresh_from_db()
        self.assertEqual(str(self.pelicula.puntuacion), "9.0")
        self.assertEqual(self.pelicula.sinopsis, "Una nueva sinopsis.")

    def test_eliminar_requiere_confirmacion_por_post(self):
        url = reverse("peliculas:eliminar", args=[self.pelicula.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Pelicula.objects.filter(pk=self.pelicula.pk).exists())

        response = self.client.post(url)
        self.assertRedirects(response, reverse("peliculas:lista"))
        self.assertFalse(Pelicula.objects.filter(pk=self.pelicula.pk).exists())

    def test_detalle_muestra_datos_de_pelicula(self):
        response = self.client.get(
            reverse("peliculas:detalle", args=[self.pelicula.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Denis Villeneuve")
        self.assertContains(response, "Ciencia ficción")
