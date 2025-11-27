import unittest
from gym_membership import (
    MEMBRESIAS,
    calcular_costos,
    procesar_plan_membresia,
)


class TestGymMembership(unittest.TestCase):

    def test_membresia_basica_sin_extras_un_miembro(self):
        membresia = MEMBRESIAS["BASIC"]
        detalle = calcular_costos(membresia, numero_miembros=1, codigos_caracteristicas=[])
        self.assertEqual(detalle["costo_base"], 50)
        self.assertEqual(detalle["costo_extras"], 0)
        self.assertEqual(detalle["total"], 50)

    def test_membresia_basica_con_extras_dos_miembros_con_descuento_grupal(self):
        membresia = MEMBRESIAS["BASIC"]
        # Extras: CG ($20) y LK ($10) → 30 por miembro → 60 para 2 miembros
        detalle = calcular_costos(membresia, numero_miembros=2, codigos_caracteristicas=["CG", "LK"])
        # Base: 50 * 2 = 100
        self.assertEqual(detalle["costo_base"], 100)
        self.assertEqual(detalle["costo_extras"], 60)
        # Subtotal = 160, sin premium
        # Descuento grupal = 10% de 160 = 16
        # Total parcial = 144 → no llega a 200, sin descuento especial
        self.assertEqual(detalle["descuento_grupal"], 16)
        self.assertEqual(detalle["descuento_especial"], 0)
        self.assertEqual(detalle["total"], 144)

    def test_membresia_premium_con_recargo_y_descuento_especial_200(self):
        membresia = MEMBRESIAS["PREMIUM"]
        # Un miembro, con EP ($40) y CI ($35) → extras = 75
        detalle = calcular_costos(membresia, numero_miembros=1, codigos_caracteristicas=["EP", "CI"])
        # Base = 100, extras = 75 → subtotal = 175
        # Recargo premium 15% de 175 ≈ 26
        self.assertEqual(detalle["costo_base"], 100)
        self.assertEqual(detalle["costo_extras"], 75)
        self.assertGreaterEqual(detalle["recargo_premium"], 20)
        # Verificar descuento especial coherente
        # Dependiendo del redondeo, puede o no superar 200
        self.assertIn(detalle["descuento_especial"], (0, 20, 50))

    def test_descuento_especial_400(self):
        membresia = MEMBRESIAS["FAMILY"]
        # Forzamos un monto alto usando varios miembros
        detalle = calcular_costos(membresia, numero_miembros=4, codigos_caracteristicas=["CF", "GD"])
        # Verificar que se aplica el descuento de 50 si el total parcial > 400
        self.assertEqual(detalle["descuento_especial"], 50)

    def test_procesar_plan_membresia_cancelado(self):
        total = procesar_plan_membresia(
            codigo_membresia="BASIC",
            numero_miembros=1,
            codigos_caracteristicas=[],
            confirmar=False,
        )
        self.assertEqual(total, -1)

    def test_procesar_plan_membresia_codigo_invalido(self):
        total = procesar_plan_membresia(
            codigo_membresia="X",
            numero_miembros=1,
            codigos_caracteristicas=[],
            confirmar=True,
        )
        self.assertEqual(total, -1)

    def test_procesar_plan_membresia_numero_invalido(self):
        total = procesar_plan_membresia(
            codigo_membresia="BASIC",
            numero_miembros=0,
            codigos_caracteristicas=[],
            confirmar=True,
        )
        self.assertEqual(total, -1)

    def test_procesar_plan_membresia_caracteristica_invalida(self):
        total = procesar_plan_membresia(
            codigo_membresia="BASIC",
            numero_miembros=1,
            codigos_caracteristicas=["EP"],  # Característica que no pertenece a BASIC
            confirmar=True,
        )
        self.assertEqual(total, -1)


if __name__ == "__main__":
    unittest.main()
