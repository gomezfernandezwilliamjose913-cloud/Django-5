from django import forms

from .models import Categoria, MovimientoStock, Producto


class MovimientoStockForm(forms.ModelForm):
    tipo = forms.ChoiceField(
        choices=[
            (MovimientoStock.Tipo.ENTRADA, "Entrada"),
            (MovimientoStock.Tipo.SALIDA, "Salida"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = MovimientoStock
        fields = ["tipo", "cantidad", "notas"]
        widgets = {
            "notas": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Motivo o referencia (opcional)",
                }
            ),
        }

    cantidad = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "min": 1}),
    )


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nombre", "descripcion"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Ej. Accesorios"}
            ),
            "descripcion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descripción breve (opcional)",
                }
            ),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre",
            "categoria",
            "descripcion",
            "precio",
            "stock",
            "stock_minimo",
        ]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del producto",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Descripción detallada",
                }
            ),
            "precio": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "stock": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
            "stock_minimo": forms.NumberInput(
                attrs={"class": "form-control", "min": 0}
            ),
            "categoria": forms.Select(attrs={"class": "form-select"}),
        }
