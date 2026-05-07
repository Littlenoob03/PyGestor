import json
import os
from typing import List, Optional
from backend.models import Cliente, Factura, Gasto

DB_FILE = "gestorpro_data.json"

class Database:
    def __init__(self):
        self.clientes: List[Cliente] = []
        self.facturas: List[Factura] = []
        self.gastos: List[Gasto] = []
        self.load()

    # ── Persistencia ──────────────────────────────────────
    def load(self):
        if not os.path.exists(DB_FILE):
            return
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.clientes = [Cliente(**c) for c in data.get("clientes", [])]
            self.facturas = [Factura(**f) for f in data.get("facturas", [])]
            self.gastos   = [Gasto(**g)   for g in data.get("gastos",   [])]
        except Exception as e:
            print(f"Error al cargar DB: {e}")

    def save(self):
        data = {
            "clientes": [c.__dict__ for c in self.clientes],
            "facturas": [f.__dict__ for f in self.facturas],
            "gastos":   [g.__dict__ for g in self.gastos],
        }
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ── IDs ───────────────────────────────────────────────
    def _next_id(self, lst) -> int:
        return max((x.id for x in lst), default=0) + 1

    # ── Clientes CRUD ─────────────────────────────────────
    def add_cliente(self, **kwargs) -> Cliente:
        c = Cliente(id=self._next_id(self.clientes), **kwargs)
        self.clientes.append(c)
        self.save()
        return c

    def update_cliente(self, id: int, **kwargs) -> Optional[Cliente]:
        c = self.get_cliente(id)
        if c:
            for k, v in kwargs.items():
                setattr(c, k, v)
            self.save()
        return c

    def delete_cliente(self, id: int):
        self.clientes = [c for c in self.clientes if c.id != id]
        self.save()

    def get_cliente(self, id: int) -> Optional[Cliente]:
        return next((c for c in self.clientes if c.id == id), None)

    # ── Facturas CRUD ─────────────────────────────────────
    def add_factura(self, **kwargs) -> Factura:
        f = Factura(id=self._next_id(self.facturas), **kwargs)
        self.facturas.append(f)
        self.save()
        return f

    def update_factura(self, id: int, **kwargs) -> Optional[Factura]:
        f = self.get_factura(id)
        if f:
            for k, v in kwargs.items():
                setattr(f, k, v)
            self.save()
        return f

    def delete_factura(self, id: int):
        self.facturas = [f for f in self.facturas if f.id != id]
        self.save()

    def get_factura(self, id: int) -> Optional[Factura]:
        return next((f for f in self.facturas if f.id == id), None)

    def facturas_by_year(self, year: int) -> List[Factura]:
        return [f for f in self.facturas if f.year == year]

    def facturas_by_trimestre(self, year: int, t: int) -> List[Factura]:
        return [f for f in self.facturas_by_year(year) if f.trimestre == t]

    # ── Gastos CRUD ───────────────────────────────────────
    def add_gasto(self, **kwargs) -> Gasto:
        g = Gasto(id=self._next_id(self.gastos), **kwargs)
        self.gastos.append(g)
        self.save()
        return g

    def update_gasto(self, id: int, **kwargs) -> Optional[Gasto]:
        g = self.get_gasto(id)
        if g:
            for k, v in kwargs.items():
                setattr(g, k, v)
            self.save()
        return g

    def delete_gasto(self, id: int):
        self.gastos = [g for g in self.gastos if g.id != id]
        self.save()

    def get_gasto(self, id: int) -> Optional[Gasto]:
        return next((g for g in self.gastos if g.id == id), None)

    def gastos_by_year(self, year: int) -> List[Gasto]:
        return [g for g in self.gastos if g.year == year]

    def gastos_by_trimestre(self, year: int, t: int) -> List[Gasto]:
        return [g for g in self.gastos_by_year(year) if g.trimestre == t]

    # ── Datos de demo ─────────────────────────────────────
    def seed_demo_data(self):
        if self.clientes:
            return  # Ya hay datos
        c1 = self.add_cliente(nombre="Tech Solutions SL",   nif="B12345678", email="info@techsolutions.es",  telefono="+34 91 123 4567", direccion="Calle Mayor 10, Madrid")
        c2 = self.add_cliente(nombre="Diseño Creativo SA",  nif="A87654321", email="contacto@disenio.es",    telefono="+34 93 987 6543", direccion="Paseo de Gracia 55, Barcelona")
        c3 = self.add_cliente(nombre="Marketing Digital SL",nif="B11223344", email="hola@mktdigital.es",     telefono="+34 96 555 1234", direccion="Gran Vía 20, Valencia")

        self.add_factura(numero="FAC-2025-001", cliente_id=c1.id, concepto="Desarrollo web corporativo",  fecha="2025-01-15", base=3000, iva_pct=21, irpf_pct=15, estado="pagado")
        self.add_factura(numero="FAC-2025-002", cliente_id=c2.id, concepto="Diseño de logotipo",          fecha="2025-02-10", base=800,  iva_pct=21, irpf_pct=15, estado="pagado")
        self.add_factura(numero="FAC-2025-003", cliente_id=c3.id, concepto="Campaña Google Ads",          fecha="2025-03-05", base=1500, iva_pct=21, irpf_pct=15, estado="pagado")
        self.add_factura(numero="FAC-2025-004", cliente_id=c1.id, concepto="Mantenimiento web - Abril",   fecha="2025-04-01", base=500,  iva_pct=21, irpf_pct=15, estado="pagado")
        self.add_factura(numero="FAC-2025-005", cliente_id=c2.id, concepto="Diseño catálogo digital",     fecha="2025-04-20", base=1200, iva_pct=21, irpf_pct=15, estado="pendiente")
        self.add_factura(numero="FAC-2025-006", cliente_id=c3.id, concepto="Consultoría SEO",             fecha="2025-05-15", base=900,  iva_pct=21, irpf_pct=15, estado="pendiente")

        self.add_gasto(descripcion="Adobe Creative Cloud",    categoria="software",   fecha="2025-01-05", base=57.64, iva_pct=21, deducible=True)
        self.add_gasto(descripcion="Material de oficina",     categoria="oficina",    fecha="2025-01-20", base=45,    iva_pct=21, deducible=True)
        self.add_gasto(descripcion="Curso marketing digital", categoria="formacion",  fecha="2025-02-12", base=297,   iva_pct=21, deducible=True)
        self.add_gasto(descripcion="Dominio y hosting",       categoria="software",   fecha="2025-02-28", base=120,   iva_pct=21, deducible=True)
        self.add_gasto(descripcion="Desplazamiento cliente",  categoria="transporte", fecha="2025-03-10", base=35,    iva_pct=0,  deducible=True)
        self.add_gasto(descripcion="Seguro RC Profesional",   categoria="seguro",     fecha="2025-04-01", base=400,   iva_pct=0,  deducible=True)