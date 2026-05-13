from typing import List, Dict, Tuple
from backend.models import Factura, Gasto

def fmt(n: float) -> str:
    """Formatea un número como moneda española."""
    return f"{n:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_resumen(facturas: List[Factura], gastos: List[Gasto]) -> Dict:
    total_base    = sum(f.base for f in facturas)
    total_gastos  = sum(g.base for g in gastos if g.deducible)
    iva_repercutido = sum(f.iva for f in facturas)
    iva_soportado   = sum(g.iva for g in gastos if g.deducible)
    irpf_retenido   = sum(f.irpf for f in facturas)
    beneficio       = total_base - total_gastos
    return {
        "total_ingresos":    total_base,
        "total_gastos":      total_gastos,
        "beneficio":         beneficio,
        "iva_repercutido":   iva_repercutido,
        "iva_soportado":     iva_soportado,
        "iva_neto":          iva_repercutido - iva_soportado,
        "irpf_retenido":     irpf_retenido,
        "irpf_estimado":     beneficio * 0.20,
        "pendientes":        sum(1 for f in facturas if f.estado == "pendiente"),
    }

def calcular_trimestre(facturas: List[Factura], gastos: List[Gasto], t: int) -> Dict:
    f_t = [f for f in facturas if f.trimestre == t]
    g_t = [g for g in gastos   if g.trimestre == t and g.deducible]
    base_i  = sum(f.base for f in f_t)
    base_g  = sum(g.base for g in g_t)
    iva_rep = sum(f.iva  for f in f_t)
    iva_sop = sum(g.iva  for g in g_t)
    irpf_ret = sum(f.irpf for f in f_t)
    beneficio = base_i - base_g
    return {
        "trimestre":     t,
        "base_ingresos": base_i,
        "base_gastos":   base_g,
        "iva_rep":       iva_rep,
        "iva_sop":       iva_sop,
        "iva_neto":      iva_rep - iva_sop,
        "irpf_retenido": irpf_ret,
        "beneficio":     beneficio,
        "modelo_130":    max(beneficio * 0.20 - irpf_ret, 0),
    }

def calcular_cuota_autonomos(rendimiento_neto_mensual: float) -> Tuple[str, float]:
    """
    Devuelve (descripción_tramo, cuota_mensual) según
    el sistema de cotización por ingresos reales 2025.
    """
    tramos = [
        (670,   "< 670 €/mes",           225),
        (900,   "670 – 900 €/mes",        250),
        (1125,  "900 – 1.125 €/mes",      267),
        (1300,  "1.125 – 1.300 €/mes",    291),
        (1500,  "1.300 – 1.500 €/mes",    294),
        (1700,  "1.500 – 1.700 €/mes",    294),
        (1850,  "1.700 – 1.850 €/mes",    350),
        (2030,  "1.850 – 2.030 €/mes",    370),
        (2330,  "2.030 – 2.330 €/mes",    390),
        (2760,  "2.330 – 2.760 €/mes",    415),
        (3190,  "2.760 – 3.190 €/mes",    465),
        (3620,  "3.190 – 3.620 €/mes",    490),
    ]
    for limite, desc, cuota in tramos:
        if rendimiento_neto_mensual < limite:
            return desc, cuota
    return "> 3.620 €/mes", 530

def ingresos_por_mes(facturas: List[Factura]) -> List[float]:
    meses = [0.0] * 12
    for f in facturas:
        meses[f.month - 1] += f.base
    return meses

def gastos_por_mes(gastos: List[Gasto]) -> List[float]:
    meses = [0.0] * 12
    for g in gastos:
        meses[g.month - 1] += g.base
    return meses


def gastos_por_categoria(gastos: List[Gasto]) -> Dict[str, float]:
    resultado = {}
    for g in gastos:
        resultado[g.categoria] = resultado.get(g.categoria, 0) + g.base
    return resultado