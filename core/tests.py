from django.test import TestCase
from django.urls import reverse

from .models import Categoria, MovimientoStock, Producto


class InventarioTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Tecnología")
        self.producto = Producto.objects.create(
            nombre="Teclado",
            descripcion="Teclado inalámbrico",
            categoria=self.categoria,
            precio="50.00",
            stock=3,
        )
        self.otro_producto = Producto.objects.create(
            nombre="Monitor",
            precio="200.00",
            stock=12,
        )

    def test_panel_muestra_resumen_y_alerta_stock_bajo(self):
        response = self.client.get(reverse("core:lista_productos"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_productos"], 2)
        self.assertEqual(response.context["total_unidades"], 15)
        self.assertEqual(response.context["productos_stock_bajo"], 1)
        self.assertContains(response, "Teclado")
        self.assertContains(response, "Stock bajo")

    def test_busqueda_por_categoria_y_filtro_stock(self):
        response = self.client.get(
            reverse("core:lista_productos"),
            {"q": "Tecnología", "stock": "bajo"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["productos"]), [self.producto])

    def test_crear_categoria_y_producto(self):
        response = self.client.post(
            reverse("core:crear_categoria"),
            {"nombre": "Hogar", "descripcion": "Artículos para el hogar"},
        )

        self.assertRedirects(response, reverse("core:lista_categorias"))
        hogar = Categoria.objects.get(nombre="Hogar")

        response = self.client.post(
            reverse("core:crear_producto"),
            {
                "nombre": "Lámpara",
                "categoria": hogar.pk,
                "descripcion": "Lámpara de escritorio",
                "precio": "25.50",
                "stock": "8",
                "stock_minimo": "4",
            },
        )

        self.assertRedirects(response, reverse("core:lista_productos"))
        self.assertTrue(Producto.objects.filter(nombre="Lámpara", categoria=hogar).exists())
        movimiento = MovimientoStock.objects.get(nombre_producto="Lámpara")
        self.assertEqual(movimiento.cantidad, 8)
        self.assertEqual(movimiento.stock_nuevo, 8)

    def test_eliminar_categoria_conserva_productos(self):
        response = self.client.post(
            reverse("core:eliminar_categoria", args=[self.categoria.pk])
        )

        self.assertRedirects(response, reverse("core:lista_categorias"))
        self.producto.refresh_from_db()
        self.assertIsNone(self.producto.categoria)

    def test_umbral_de_stock_minimo_es_configurable(self):
        self.producto.stock_minimo = 3
        self.producto.save(update_fields=["stock_minimo"])

        response = self.client.get(
            reverse("core:lista_productos"),
            {"stock": "bajo"},
        )

        self.assertEqual(list(response.context["productos"]), [self.producto])
        self.assertEqual(response.context["productos_stock_bajo"], 1)

    def test_lista_se_puede_ordenar_por_precio(self):
        response = self.client.get(
            reverse("core:lista_productos"),
            {"orden": "precio"},
        )

        self.assertEqual(
            list(response.context["productos"]),
            [self.producto, self.otro_producto],
        )

    def test_exportacion_csv_respeta_busqueda(self):
        response = self.client.get(
            reverse("core:exportar_productos"),
            {"q": "Teclado"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Disposition"],
            'attachment; filename="inventario.csv"',
        )
        self.assertIn("Teclado", response.content.decode("utf-8-sig"))
        self.assertNotIn("Monitor", response.content.decode("utf-8-sig"))

    def test_entrada_y_salida_registran_historial_y_actualizan_stock(self):
        url = reverse("core:movimientos_producto", args=[self.producto.pk])

        response = self.client.post(
            url,
            {"tipo": "entrada", "cantidad": "4", "notas": "Reposición"},
        )
        self.assertRedirects(response, url)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 7)

        response = self.client.post(
            url,
            {"tipo": "salida", "cantidad": "2", "notas": "Venta"},
        )
        self.assertRedirects(response, url)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 5)
        self.assertEqual(self.producto.movimientos.count(), 2)

    def test_salida_no_permite_stock_negativo(self):
        response = self.client.post(
            reverse("core:movimientos_producto", args=[self.producto.pk]),
            {"tipo": "salida", "cantidad": "4", "notas": "Venta"},
        )

        self.assertEqual(response.status_code, 200)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 3)
        self.assertEqual(self.producto.movimientos.count(), 0)
        self.assertContains(response, "solo hay 3 disponibles")

    def test_editar_stock_registra_ajuste(self):
        response = self.client.post(
            reverse("core:editar_producto", args=[self.producto.pk]),
            {
                "nombre": "Teclado",
                "categoria": self.categoria.pk,
                "descripcion": "Teclado inalámbrico",
                "precio": "50.00",
                "stock": "6",
                "stock_minimo": "3",
            },
        )

        self.assertRedirects(response, reverse("core:lista_productos"))
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 6)
        movimiento = MovimientoStock.objects.get(producto=self.producto)
        self.assertEqual(movimiento.tipo, MovimientoStock.Tipo.AJUSTE)
        self.assertEqual(movimiento.stock_anterior, 3)
        self.assertEqual(movimiento.stock_nuevo, 6)

    def test_eliminar_producto_conserva_el_historial(self):
        MovimientoStock.objects.create(
            producto=self.producto,
            nombre_producto=self.producto.nombre,
            tipo=MovimientoStock.Tipo.ENTRADA,
            cantidad=3,
            stock_anterior=0,
            stock_nuevo=3,
        )

        response = self.client.post(
            reverse("core:eliminar_producto", args=[self.producto.pk])
        )

        self.assertRedirects(response, reverse("core:lista_productos"))
        movimiento = MovimientoStock.objects.get()
        self.assertIsNone(movimiento.producto)
        self.assertEqual(movimiento.nombre_producto, "Teclado")
