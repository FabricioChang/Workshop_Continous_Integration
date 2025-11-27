"""
Sistema de Gestión de Membresías de Gimnasio (CLI)

Requisitos cubiertos:
- Selección de membresía
- Características adicionales por membresía
- Cálculo de costos (base + extras)
- Descuento por grupo (>= 2 miembros)
- Descuentos especiales por monto total
- Recargo por membresía premium
- Validación de disponibilidad
- Confirmación del usuario
- Devolver costo total (entero positivo) o -1 si es inválido / cancelado
- Manejo básico de errores con mensajes descriptivos
"""

from dataclasses import dataclass
from typing import List, Dict, Tuple


# ------------------------ MODELO DE DATOS ------------------------ #

@dataclass
class Membresia:
    codigo: str
    nombre: str
    precio_base: int
    es_premium: bool
    caracteristicas: Dict[str, int]  # clave: código de característica, valor: costo


# Definición de los planes de membresía y sus características adicionales
MEMBRESIAS: Dict[str, Membresia] = {
    "BASIC": Membresia(
        codigo="BASIC",
        nombre="Básica",
        precio_base=50,
        es_premium=False,
        caracteristicas={
            "CG": 20,  # Clases grupales
            "LK": 10,  # Lockers
        },
    ),
    "PREMIUM": Membresia(
        codigo="PREMIUM",
        nombre="Premium",
        precio_base=100,
        es_premium=True,
        caracteristicas={
            "EP": 40,  # Entrenador personal
            "SPA": 30,  # Spa / zona de relax
            "CI": 35,  # Clases ilimitadas
        },
    ),
    "FAMILY": Membresia(
        codigo="FAMILY",
        nombre="Familiar",
        precio_base=150,
        es_premium=False,
        caracteristicas={
            "CF": 30,  # Clases familiares
            "GD": 25,  # Guardería
        },
    ),
}


# ------------------------ LÓGICA DE NEGOCIO ------------------------ #

def calcular_costos(
    membresia: Membresia,
    numero_miembros: int,
    codigos_caracteristicas: List[str],
) -> Dict[str, int]:
    """
    Calcula el detalle de costos de la membresía.

    Orden de cálculo (elegido y documentado para el informe):
    1. Costo base = precio_base * número de miembros
    2. Costo extras = suma de extras * número de miembros
       (Suposición: todos los miembros del grupo tienen las mismas características adicionales)
    3. Subtotal = base + extras
    4. Si es premium: recargo 15% sobre el subtotal
    5. Descuento grupal (10%) si hay 2 o más miembros (después del recargo premium)
    6. Descuento especial:
       - Si total > 400 → -50
       - Si total > 200 → -20
       (Se aplica solo uno, el de mayor valor posible)
    """

    if numero_miembros <= 0:
        raise ValueError("El número de miembros debe ser mayor que 0.")

    # Validar características
    for cod in codigos_caracteristicas:
        if cod not in membresia.caracteristicas:
            raise ValueError(f"Característica no disponible para esta membresía: {cod}")

    # 1. Costo base
    costo_base = membresia.precio_base * numero_miembros

    # 2. Costo de características adicionales (por miembro)
    costo_extra_por_miembro = 0
    for cod in codigos_caracteristicas:
        costo_extra_por_miembro += membresia.caracteristicas[cod]

    costo_extras = costo_extra_por_miembro * numero_miembros

    # 3. Subtotal
    subtotal = costo_base + costo_extras

    # 4. Recargo premium (15%)
    recargo_premium = 0
    if membresia.es_premium:
        recargo_premium = int(round(subtotal * 0.15))
        subtotal_con_recargo = subtotal + recargo_premium
    else:
        subtotal_con_recargo = subtotal

    # 5. Descuento grupal (10%) si 2 o más miembros
    descuento_grupal = 0
    if numero_miembros >= 2:
        descuento_grupal = int(round(subtotal_con_recargo * 0.10))
        total_parcial = subtotal_con_recargo - descuento_grupal
    else:
        total_parcial = subtotal_con_recargo

    # 6. Descuento especial por monto
    descuento_especial = 0
    if total_parcial > 400:
        descuento_especial = 50
    elif total_parcial > 200:
        descuento_especial = 20

    total_final = total_parcial - descuento_especial

    # Garantizar entero positivo
    if total_final < 0:
        total_final = 0

    return {
        "costo_base": costo_base,
        "costo_extras": costo_extras,
        "recargo_premium": recargo_premium,
        "descuento_grupal": descuento_grupal,
        "descuento_especial": descuento_especial,
        "total": int(total_final),
    }


def procesar_plan_membresia(
    codigo_membresia: str,
    numero_miembros: int,
    codigos_caracteristicas: List[str],
    confirmar: bool,
) -> int:
    """
    Función "pura" para pruebas y para cumplir con el requisito:
    - Devuelve el costo total (entero positivo) si todo es válido y confirmado.
    - Devuelve -1 si:
      * La membresía no existe
      * Hay características inválidas
      * El número de miembros es inválido
      * El usuario cancela (confirmar == False)
    """

    if not confirmar:
        # El usuario cancela el plan
        return -1

    membresia = MEMBRESIAS.get(codigo_membresia.upper())
    if membresia is None:
        return -1

    try:
        detalle = calcular_costos(membresia, numero_miembros, codigos_caracteristicas)
    except ValueError:
        return -1

    # Devolver el total (entero positivo)
    return detalle["total"]


# ------------------------ INTERFAZ DE CONSOLA (CLI) ------------------------ #

def mostrar_membresias():
    print("\n=== PLANES DE MEMBRESÍA DISPONIBLES ===")
    for m in MEMBRESIAS.values():
        tipo = " (Premium)" if m.es_premium else ""
        print(f"- {m.codigo}: {m.nombre}{tipo} - Precio base por miembro: ${m.precio_base}")


def mostrar_caracteristicas(membresia: Membresia):
    print(f"\nCaracterísticas adicionales para el plan {membresia.nombre}:")
    if not membresia.caracteristicas:
        print("   No hay características adicionales disponibles.")
        return
    for cod, costo in membresia.caracteristicas.items():
        descripcion = {
            "CG": "Clases grupales",
            "LK": "Uso de lockers",
            "EP": "Entrenador personal",
            "SPA": "Acceso a spa / zona relax",
            "CI": "Clases ilimitadas",
            "CF": "Clases familiares",
            "GD": "Guardería",
        }.get(cod, f"Opción {cod}")
        print(f"   {cod} - {descripcion}: ${costo} por miembro")


def leer_entero_positivo(mensaje: str) -> int:
    while True:
        entrada = input(mensaje)
        try:
            valor = int(entrada)
            if valor <= 0:
                print("⚠ Por favor, ingresa un número entero positivo.")
            else:
                return valor
        except ValueError:
            print("⚠ Entrada no válida. Debes ingresar un número entero.")


def leer_codigos_caracteristicas(membresia: Membresia) -> List[str]:
    if not membresia.caracteristicas:
        return []

    print("\nIngresa los códigos de las características adicionales separadas por coma.")
    print("O ingresa '0' si no deseas agregar características.")
    entrada = input("Características: ").strip()

    if entrada == "0" or entrada == "":
        return []

    partes = [p.strip().upper() for p in entrada.split(",") if p.strip() != ""]

    # Validación básica aquí (aunque la validación completa la hace calcular_costos)
    codigos_validos = []
    for cod in partes:
        if cod in membresia.caracteristicas:
            codigos_validos.append(cod)
        else:
            print(f"⚠ Advertencia: '{cod}' no es una característica válida para este plan y será ignorada.")

    return codigos_validos


def ejecutar_cli() -> int:
    """
    Ejecuta la aplicación de consola completa.
    Devuelve:
    - total a pagar (entero positivo) si el usuario confirma
    - -1 si el usuario cancela o si ocurre un problema grave
    """
    print("===============================================")
    print("  SISTEMA DE GESTIÓN DE MEMBRESÍAS DE GIMNASIO ")
    print("===============================================")

    # 1. Selección de membresía
    while True:
        mostrar_membresias()
        cod = input("\nIngresa el CÓDIGO de la membresía que deseas (por ejemplo BASIC): ").strip().upper()
        membresia = MEMBRESIAS.get(cod)
        if membresia is None:
            print("❌ Membresía no válida. Intenta nuevamente.")
        else:
            break

    # 2. Número de miembros
    num_miembros = leer_entero_positivo("Ingresa el número de miembros que se afiliarán con este plan: ")

    # 3. Características adicionales
    mostrar_caracteristicas(membresia)
    codigos_caracteristicas = leer_codigos_caracteristicas(membresia)

    # 4. Cálculo de costos
    try:
        detalle = calcular_costos(membresia, num_miembros, codigos_caracteristicas)
    except ValueError as e:
        print(f"❌ Error en los datos ingresados: {e}")
        print("El plan no es válido. Saliendo...")
        return -1

    # 5. Mostrar resumen para confirmación
    print("\n=========== RESUMEN DEL PLAN SELECCIONADO ===========")
    print(f"Plan: {membresia.nombre} ({membresia.codigo})")
    print(f"Número de miembros: {num_miembros}")
    print(f"Costo base total: ${detalle['costo_base']}")
    print(f"Costo características adicionales: ${detalle['costo_extras']}")
    print(f"Recargo premium (15%): ${detalle['recargo_premium']}")
    print(f"Descuento por grupo (10%): -${detalle['descuento_grupal']}")
    print(f"Descuento especial: -${detalle['descuento_especial']}")
    print(f"TOTAL A PAGAR: ${detalle['total']}")
    print("=====================================================")

    confirmar_str = input("¿Deseas confirmar este plan? (S/N): ").strip().upper()
    if confirmar_str != "S":
        print("Has cancelado el plan. No se ha realizado ningún cobro.")
        return -1

    print(f"\n✅ Plan confirmado. Total a pagar: ${detalle['total']}")
    return detalle["total"]


if __name__ == "__main__":
    # Permite usar el archivo directamente desde la consola.
    ejecutar_cli()
