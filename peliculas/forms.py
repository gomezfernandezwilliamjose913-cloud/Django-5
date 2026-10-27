from django import forms

from .models import Pelicula


class PeliculaForm(forms.ModelForm):
    class Meta:
        model = Pelicula
        fields = [
            "titulo",
            "director",
            "genero",
            "anio",
            "duracion",
            "puntuacion",
            "estado",
            "imagen_url",
            "sinopsis",
        ]
        widgets = {
            "titulo": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ej. El viaje de Chihiro"}
            ),
            "director": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Nombre del director"}
            ),
            "genero": forms.Select(attrs={"class": "form-select"}),
            "anio": forms.NumberInput(
                attrs={"class": "form-control", "min": 1888, "max": 2100}
            ),
            "duracion": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "placeholder": "120"}
            ),
            "puntuacion": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "max": 10,
                    "step": "0.1",
                    "placeholder": "8.5",
                }
            ),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "imagen_url": forms.URLInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "https://ejemplo.com/poster.jpg",
                }
            ),
            "sinopsis": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "¿De qué trata la película?",
                }
            ),
        }
