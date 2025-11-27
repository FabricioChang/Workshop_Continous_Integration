"""
Pruebas del sistema de membresías usando pytest y pylint.

Requisitos verificados:
- Cálculo de costo base
- Cálculo de extras
- Descuento por grupo (>= 2 miembros)
- Descuentos especiales ($20 y $50)
- Recargo premium (15%)
- Manejo de entradas inválidas
- Devolución de -1 en casos inválidos o cancelados
- Revisión de estilo con pylint sobre gym_membership.py
"""

import sys
import subprocess
from pathlib import Path

import pytest

from gym_membership import (
    MEMBRESIAS,
    calcular_costos,
    procesar_plan_membresia,
)


# ---------------------- PRUEBAS FUNCIONALES (PYTEST) ---------------------- #


def test_basica_un_miembro_sin_extras():
    """
    Caso base: membresía BASIC, 1 miembro, sin características adicionales.
    Debe calcular correctamente el costo base sin descuentos ni recargos.
    """
    membresia = MEMBRESIAS["BASIC"]
    detalle = calcular_costos(membresia, numero_miembros=1, codigos_caracteristicas=[])

    assert detalle["costo_base"] == 50
    assert detalle["costo_extras"] == 0
    assert detalle["recargo_premium"] == 0
    assert detalle["descuento_grupal"] == 0
    assert detalle["descuento_especial"] == 0
    assert detalle["total"] == 50


def test_basica_dos_miembros_con_extras_y_descuento_grupal():
    """
    Membresía BASIC con 2 miembros y características adicionales.
    Verifica:
    - Cálculo de costo base + extras
    - Aplicación de 10% de descuento por grupo
    - Sin descuento especial por monto
    """
    membresia = MEMBRESIAS["BASIC"]
    # Extras: CG (20) + LK (10) = 30 por miembro → 60 para 2 miembros
    detalle = calcular_costos(
        membresia,
        numero_miembros=2,
        codigos_caracteristicas=["CG", "LK"],
    )

    # Base: 50 * 2 = 100
    # Extras: 30 * 2 = 60
    # Subtotal = 160
    # Descuento grupal 10% = 16
    # Total = 144
    assert detalle["costo_base"] == 100
    assert detalle["costo_extras"] == 60
    assert detalle["recargo_premium"] == 0
    assert detalle["descuento_grupal"] == 16
    assert detalle["descuento_especial"] == 0
    assert detalle["total"] == 144


def test_premium_un_miembro_con_extras_recargo_y_descuento_especial_200():
    """
    Membresía PREMIUM con 1 miembro y dos extras.
    Verifica:
    - Recargo premium de 15%
    - Descuento especial de 20 si el total supera 200
    """
    membresia = MEMBRESIAS["PREMIUM"]
    # Extras: EP (40) + CI (35) = 75 por miembro
    detalle = calcular_costos(
        membresia,
        numero_miembros=1,
        codigos_caracteristicas=["EP", "CI"],
    )

    # Base: 100
    # Extras: 75
    # Subtotal = 175
    # Recargo premium 15% = 26 (round)
    # Subtotal con recargo = 201
    # Descuento especial: >200 → 20
    # Total = 181
    assert detalle["costo_base"] == 100
    assert detalle["costo_extras"] == 75
    assert detalle["recargo_premium"] == 26
    assert detalle["descuento_grupal"] == 0
    assert detalle["descuento_especial"] == 20
    assert detalle["total"] == 181


def test_family_cuatro_miembros_con_extras_y_descuento_especial_400():
    """
    Membresía FAMILY con 4 miembros y dos extras.
    Verifica:
    - Descuento por grupo (10%)
    - Descuento especial de 50 si el total supera 400
    """
    membresia = MEMBRESIAS["FAMILY"]
    # Extras: CF (30) + GD (25) = 55 por miembro
    detalle = calcular_costos(
        membresia,
        numero_miembros=4,
        codigos_caracteristicas=["CF", "GD"],
    )

    # Base: 150 * 4 = 600
    # Extras: 55 * 4 = 220
    # Subtotal = 820
    # Descuento grupal 10% de 820 = 82
    # Parcial = 738
    # Descuento especial: >400 → 50
    # Total = 688
    assert detalle["costo_base"] == 600
    assert detalle["costo_extras"] == 220
    assert detalle["recargo_premium"] == 0
    assert detalle["descuento_grupal"] == 82
    assert detalle["descuento_especial"] == 50
    assert detalle["total"] == 688


def test_calcular_costos_numero_miembros_invalido():
    """
    Si el número de miembros es <= 0, calcular_costos debe lanzar ValueError.
    """
    membresia = MEMBRESIAS["BASIC"]
    with pytest.raises(ValueError):
        calcular_costos(membresia, numero_miembros=0, codigos_caracteristicas=[])


def test_calcular_costos_caracteristica_invalida():
    """
    Si se ingresa una característica que no pertenece a la membresía,
    calcular_costos debe lanzar ValueError.
    """
    membresia = MEMBRESIAS["BASIC"]
    # "EP" solo es válido para PREMIUM, no para BASIC
    with pytest.raises(ValueError):
        calcular_costos(membresia, numero_miembros=1, codigos_caracteristicas=["EP"])


def test_procesar_plan_membresia_cancelado():
    """
    Si el usuario no confirma (confirmar=False), el resultado debe ser -1.
    """
    total = procesar_plan_membresia(
        codigo_membresia="BASIC",
        numero_miembros=1,
        codigos_caracteristicas=[],
        confirmar=False,
    )
    assert total == -1


def test_procesar_plan_membresia_codigo_invalido():
    """
    Si el código de membresía no existe, procesar_plan_membresia debe devolver -1.
    """
    total = procesar_plan_membresia(
        codigo_membresia="XYZ",
        numero_miembros=1,
        codigos_caracteristicas=[],
        confirmar=True,
    )
    assert total == -1


def test_procesar_plan_membresia_numero_miembros_invalido():
    """
    Si el número de miembros es inválido, procesar_plan_membresia debe devolver -1.
    """
    total = procesar_plan_membresia(
        codigo_membresia="BASIC",
        numero_miembros=0,
        codigos_caracteristicas=[],
        confirmar=True,
    )
    assert total == -1


def test_procesar_plan_membresia_caracteristica_invalida():
    """
    Si se envía una característica no válida para el plan, debe devolver -1.
    """
    total = procesar_plan_membresia(
        codigo_membresia="BASIC",
        numero_miembros=1,
        codigos_caracteristicas=["EP"],  # EP no es válido para BASIC
        confirmar=True,
    )
    assert total == -1


def test_procesar_plan_membresia_valido_devuelve_entero_positivo():
    """
    Caso válido: debe devolver un entero positivo (total a pagar).
    """
    total = procesar_plan_membresia(
        codigo_membresia="PREMIUM",
        numero_miembros=2,
        codigos_caracteristicas=["EP"],
        confirmar=True,
    )
    assert isinstance(total, int)
    assert total > 0


# ---------------------- PRUEBA DE ESTILO CON PYLINT ---------------------- #


@pytest.mark.lint
def test_pylint_sobre_gym_membership():
    """
    Ejecuta pylint sobre gym_membership.py.

    - Usa subprocess para llamar a pylint.
    - Se deshabilitan algunos mensajes muy verbosos (como falta de docstring).
    - El test pasa si pylint termina con código 0 (sin errores "bloqueantes").

    Nota: requiere que pylint esté instalado en el entorno:
    pip install pylint
    """
    ruta = Path(__file__).parent / "gym_membership.py"
    assert ruta.exists(), "No se encontró gym_membership.py en el mismo directorio de tests."

    # Puedes ajustar la lista de reglas deshabilitadas según lo que te pida el docente.
    cmd = [
        sys.executable,
        "-m",
        "pylint",
        str(ruta),
        "--disable=C0114,C0115,C0116,C0301",
    ]


    resultado = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
    )

    # Imprimimos la salida para poder verla en el log de CI si algo falla
    print("=== PYLINT STDOUT ===")
    print(resultado.stdout)
    print("=== PYLINT STDERR ===")
    print(resultado.stderr)

    # pylint retorna 0 cuando no hay errores considerados "graves"
    assert resultado.returncode == 0, "pylint encontró problemas en gym_membership.py"


# Fin del archivo