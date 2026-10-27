from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Pelicula(models.Model):
    class Genero(models.TextChoices):
        ACCION = "accion", "Acción"
        ANIMACION = "animacion", "Animación"
        AVENTURA = "aventura", "Aventura"
        CIENCIA_FICCION = "ciencia_ficcion", "Ciencia ficción"
        COMEDIA = "comedia", "Comedia"
        DOCUMENTAL = "documental", "Documental"
        DRAMA = "drama", "Drama"
        FANTASIA = "fantasia", "Fantasía"
        TERROR = "terror", "Terror"
        SUSPENSO = "suspenso", "Suspenso"
        OTRO = "otro", "Otro"

    class Estado(models.TextChoices):
        PENDIENTE = "pendiente", "Pendiente"
        VIENDO = "viendo", "Viendo"
        VISTA = "vista", "Vista"

    titulo = models.CharField(max_length=150)
    director = models.CharField(max_length=120, blank=True)
    genero = models.CharField(
        max_length=20,
        choices=Genero.choices,
        default=Genero.OTRO,
    )
    anio = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1888), MaxValueValidator(2100)]
    )
    duracion = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        help_text="Duración en minutos.",
        validators=[MinValueValidator(1), MaxValueValidator(999)],
    )
    puntuacion = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Puntuación opcional, de 0 a 10.",
    )
    estado = models.CharField(
        max_length=12,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    sinopsis = models.TextField(blank=True)
    imagen_url = models.URLField("URL del póster", blank=True)
    creada_en = models.DateTimeField(auto_now_add=True)
    actualizada_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creada_en", "titulo"]
        verbose_name = "película"
        verbose_name_plural = "películas"

    def __str__(self):
        return f"{self.titulo} ({self.anio})"
