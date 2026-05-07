from dataclasses import dataclass, field
from datetime import date
from typing import Optional

@dataclass
class Cliente:
    id: int
    nombre: str
    nif: str
    email: str = ""
    telefono: str = ""
    direccion: str = ""

@dataclass
class Factura:
    id: int
    numero: str
    cliente_id: int
    concepto: str
    fecha: str          # "YYYY-MM-DD"
    base: float
    iva_pct: float      # 0, 4, 10, 21
    irpf_pct: float     # 0, 7, 15
    estado: str         # "pendiente" | "pagado"

    @property
    def iva(self) -> float:
        return round(self.base * self.iva_pct / 100, 2)

    @property
    def irpf(self) -> float:
        return round(self.base * self.irpf_pct / 100, 2)

    @property
    def total(self) -> float:
        return round(self.base + self.iva - self.irpf, 2)

    @property
    def year(self) -> int:
        return int(self.fecha[:4])

    @property
    def month(self) -> int:
        return int(self.fecha[5:7])

    @property
    def trimestre(self) -> int:
        return (self.month - 1) // 3 + 1

@dataclass
class Gasto:
    id: int
    descripcion: str
    categoria: str
    fecha: str          # "YYYY-MM-DD"
    base: float
    iva_pct: float
    deducible: bool = True

    @property
    def iva(self) -> float:
        return round(self.base * self.iva_pct / 100, 2)

    @property
    def total(self) -> float:
        return round(self.base + self.iva, 2)

    @property
    def year(self) -> int:
        return int(self.fecha[:4])

    @property
    def month(self) -> int:
        return int(self.fecha[5:7])

    @property
    def trimestre(self) -> int:
        return (self.month - 1) // 3 + 1