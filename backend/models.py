from dataclasses import dataclass, field
from datetime import date
from typing import Optional

@dataclass
class Ingreso:
    id: int
    origen: str         # Antes 'destinatario'
    concepto: str
    fecha: str          # "YYYY-MM-DD"
    importe: float
    estado: str         # "pendiente" | "cobrado"
    usuario_id: int = 1

    @property
    def total(self) -> float:
        return self.importe

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
    importe: float
    usuario_id: int = 1

    @property
    def total(self) -> float:
        return self.importe

    @property
    def year(self) -> int:
        return int(self.fecha[:4])

    @property
    def month(self) -> int:
        return int(self.fecha[5:7])

    @property
    def trimestre(self) -> int:
        return (self.month - 1) // 3 + 1