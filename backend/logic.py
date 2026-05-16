from typing import List, Dict, Tuple
from backend.models import Ingreso, Gasto

def fmt(n: float) -> str:
    """Formatea un número como moneda española."""
    return f"{n:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_resumen(ingresos: List[Ingreso], gastos: List[Gasto]) -> Dict:
    total_ing = sum(f.importe for f in ingresos)
    total_gas = sum(g.importe for g in gastos)
    beneficio = total_ing - total_gas
    return {
        "total_ingresos":    total_ing,
        "total_gastos":      total_gas,
        "beneficio":         beneficio,
        "pendientes":        sum(1 for f in ingresos if f.estado == "pendiente"),
    }

def calcular_trimestre(ingresos: List[Ingreso], gastos: List[Gasto], t: int) -> Dict:
    i_t = [f for f in ingresos if f.trimestre == t]
    g_t = [g for g in gastos   if g.trimestre == t]
    base_i  = sum(f.importe for f in i_t)
    base_g  = sum(g.importe for g in g_t)
    beneficio = base_i - base_g
    return {
        "trimestre":     t,
        "base_ingresos": base_i,
        "base_gastos":   base_g,
        "beneficio":     beneficio,
    }

def ingresos_por_mes(ingresos: List[Ingreso]) -> List[float]:
    meses = [0.0] * 12
    for f in ingresos:
        meses[f.month - 1] += f.importe
    return meses

def gastos_por_mes(gastos: List[Gasto]) -> List[float]:
    meses = [0.0] * 12
    for g in gastos:
        meses[g.month - 1] += g.importe
    return meses

def gastos_por_categoria(gastos: List[Gasto]) -> Dict[str, float]:
    resultado = {}
    for g in gastos:
        resultado[g.categoria] = resultado.get(g.categoria, 0) + g.importe
    return resultado