from dataclasses import dataclass, field
from datetime import date
from typing import Optional

@dataclass
class Ingreso:
    """Representa un movimiento de entrada de dinero en la aplicación."""
    id: int
    origen: str         
    concepto: str
    fecha: str          
    importe: float
    estado: str        
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
    """Representa un movimiento de salida de dinero (compra, recibo, etc.) en la aplicación."""
    id: int
    descripcion: str
    categoria: str
    fecha: str          
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