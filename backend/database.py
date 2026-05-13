import sqlite3
import os
from typing import List, Optional
from backend.models import Factura, Gasto

DB_FILE = "gestorpro.db"


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row   # acceso por nombre de columna
        self._create_tables()

    # ─────────────────────────────────────────────────────────
    # CREACIÓN DE TABLAS
    # ─────────────────────────────────────────────────────────
    def _create_tables(self):
        cur = self.conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username  TEXT    NOT NULL UNIQUE,
                password  TEXT    NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS facturas (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                numero       TEXT    NOT NULL,
                destinatario TEXT    NOT NULL,
                concepto     TEXT    NOT NULL,
                fecha        TEXT    NOT NULL,
                base         REAL    NOT NULL,
                iva_pct      REAL    NOT NULL DEFAULT 21,
                irpf_pct     REAL    NOT NULL DEFAULT 15,
                estado       TEXT    NOT NULL DEFAULT 'pendiente'
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT    NOT NULL,
                categoria   TEXT    NOT NULL,
                fecha       TEXT    NOT NULL,
                base        REAL    NOT NULL,
                iva_pct     REAL    NOT NULL DEFAULT 21,
                deducible   INTEGER NOT NULL DEFAULT 1   -- 1=True, 0=False
            )
        """)

        self.conn.commit()

    # ─────────────────────────────────────────────────────────
    # USUARIOS — AUTENTICACIÓN
    # ─────────────────────────────────────────────────────────
    def get_usuario(self, username, password):
        row = self.conn.execute(
            "SELECT * FROM usuarios WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        return dict(row) if row else None

    def get_usuario_by_username(self, username):
        row = self.conn.execute(
            "SELECT * FROM usuarios WHERE username = ?",
            (username,)
        ).fetchone()
        return dict(row) if row else None

    def add_usuario(self, username, password):
        try:
            self.conn.execute(
                "INSERT INTO usuarios (username, password) VALUES (?, ?)",
                (username, password)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # Usuario ya existe

    # ─────────────────────────────────────────────────────────
    # HELPERS INTERNOS
    # ─────────────────────────────────────────────────────────
    def _row_to_factura(self, row) -> Factura:
        return Factura(
            id=row["id"],
            numero=row["numero"],
            destinatario=row["destinatario"],
            concepto=row["concepto"],
            fecha=row["fecha"],
            base=row["base"],
            iva_pct=row["iva_pct"],
            irpf_pct=row["irpf_pct"],
            estado=row["estado"],
        )

    def _row_to_gasto(self, row) -> Gasto:
        return Gasto(
            id=row["id"],
            descripcion=row["descripcion"],
            categoria=row["categoria"],
            fecha=row["fecha"],
            base=row["base"],
            iva_pct=row["iva_pct"],
            deducible=bool(row["deducible"]),
        )

    # ─────────────────────────────────────────────────────────
    # FACTURAS — CRUD
    # ─────────────────────────────────────────────────────────
    def add_factura(self, numero, destinatario, concepto, fecha,
                    base, iva_pct, irpf_pct, estado="pendiente") -> Factura:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO facturas "
            "(numero, destinatario, concepto, fecha, base, iva_pct, irpf_pct, estado) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (numero, destinatario, concepto, fecha, base, iva_pct, irpf_pct, estado),
        )
        self.conn.commit()
        return self.get_factura(cur.lastrowid)

    def update_factura(self, id: int, **kwargs) -> Optional[Factura]:
        allowed = {"numero", "destinatario", "concepto", "fecha",
                   "base", "iva_pct", "irpf_pct", "estado"}
        fields  = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return self.get_factura(id)
        sets = ", ".join(f"{k} = ?" for k in fields)
        self.conn.execute(
            f"UPDATE facturas SET {sets} WHERE id = ?",
            (*fields.values(), id),
        )
        self.conn.commit()
        return self.get_factura(id)

    def delete_factura(self, id: int):
        self.conn.execute("DELETE FROM facturas WHERE id = ?", (id,))
        self.conn.commit()

    def get_factura(self, id: int) -> Optional[Factura]:
        row = self.conn.execute(
            "SELECT * FROM facturas WHERE id = ?", (id,)
        ).fetchone()
        return self._row_to_factura(row) if row else None

    @property
    def facturas(self) -> List[Factura]:
        rows = self.conn.execute(
            "SELECT * FROM facturas ORDER BY fecha DESC"
        ).fetchall()
        return [self._row_to_factura(r) for r in rows]

    def facturas_by_year(self, year: int) -> List[Factura]:
        rows = self.conn.execute(
            "SELECT * FROM facturas WHERE strftime('%Y', fecha) = ? ORDER BY fecha DESC",
            (str(year),),
        ).fetchall()
        return [self._row_to_factura(r) for r in rows]

    def facturas_by_trimestre(self, year: int, t: int) -> List[Factura]:
        # Calculamos los meses del trimestre directamente en SQL
        month_ranges = {1: ("01","03"), 2: ("04","06"),
                        3: ("07","09"), 4: ("10","12")}
        m_ini, m_fin = month_ranges[t]
        rows = self.conn.execute(
            "SELECT * FROM facturas "
            "WHERE strftime('%Y', fecha) = ? "
            "  AND strftime('%m', fecha) BETWEEN ? AND ? "
            "ORDER BY fecha DESC",
            (str(year), m_ini, m_fin),
        ).fetchall()
        return [self._row_to_factura(r) for r in rows]

    # ─────────────────────────────────────────────────────────
    # GASTOS — CRUD
    # ─────────────────────────────────────────────────────────
    def add_gasto(self, descripcion, categoria, fecha,
                  base, iva_pct, deducible=True) -> Gasto:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO gastos (descripcion, categoria, fecha, base, iva_pct, deducible) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (descripcion, categoria, fecha, base, iva_pct, int(deducible)),
        )
        self.conn.commit()
        return self.get_gasto(cur.lastrowid)

    def update_gasto(self, id: int, **kwargs) -> Optional[Gasto]:
        allowed = {"descripcion", "categoria", "fecha", "base", "iva_pct", "deducible"}
        fields  = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return self.get_gasto(id)
        # Convertir booleano a entero para SQLite
        if "deducible" in fields:
            fields["deducible"] = int(fields["deducible"])
        sets = ", ".join(f"{k} = ?" for k in fields)
        self.conn.execute(
            f"UPDATE gastos SET {sets} WHERE id = ?",
            (*fields.values(), id),
        )
        self.conn.commit()
        return self.get_gasto(id)

    def delete_gasto(self, id: int):
        self.conn.execute("DELETE FROM gastos WHERE id = ?", (id,))
        self.conn.commit()

    def get_gasto(self, id: int) -> Optional[Gasto]:
        row = self.conn.execute(
            "SELECT * FROM gastos WHERE id = ?", (id,)
        ).fetchone()
        return self._row_to_gasto(row) if row else None

    @property
    def gastos(self) -> List[Gasto]:
        rows = self.conn.execute(
            "SELECT * FROM gastos ORDER BY fecha DESC"
        ).fetchall()
        return [self._row_to_gasto(r) for r in rows]

    def gastos_by_year(self, year: int) -> List[Gasto]:
        rows = self.conn.execute(
            "SELECT * FROM gastos WHERE strftime('%Y', fecha) = ? ORDER BY fecha DESC",
            (str(year),),
        ).fetchall()
        return [self._row_to_gasto(r) for r in rows]

    def gastos_by_trimestre(self, year: int, t: int) -> List[Gasto]:
        month_ranges = {1: ("01","03"), 2: ("04","06"),
                        3: ("07","09"), 4: ("10","12")}
        m_ini, m_fin = month_ranges[t]
        rows = self.conn.execute(
            "SELECT * FROM gastos "
            "WHERE strftime('%Y', fecha) = ? "
            "  AND strftime('%m', fecha) BETWEEN ? AND ? "
            "ORDER BY fecha DESC",
            (str(year), m_ini, m_fin),
        ).fetchall()
        return [self._row_to_gasto(r) for r in rows]

    # ─────────────────────────────────────────────────────────
    # DATOS DE DEMO
    # ─────────────────────────────────────────────────────────
    def seed_demo_data(self):
        # Insert admin user if empty
        if not self.conn.execute("SELECT 1 FROM usuarios LIMIT 1").fetchone():
            self.add_usuario("admin", "admin")

        # Solo inserta facturas si la base de datos de facturas está vacía
        if self.facturas:
            return

        self.add_factura("FAC-2025-001", "Tech Solutions SL", "Desarrollo web corporativo",  "2025-01-15", 3000, 21, 15, "pagado")
        self.add_factura("FAC-2025-002", "Diseño Creativo SA", "Diseño de logotipo",          "2025-02-10",  800, 21, 15, "pagado")
        self.add_factura("FAC-2025-003", "Marketing Digital SL", "Campaña Google Ads",          "2025-03-05", 1500, 21, 15, "pagado")
        self.add_factura("FAC-2025-004", "Tech Solutions SL", "Mantenimiento web - Abril",   "2025-04-01",  500, 21, 15, "pagado")
        self.add_factura("FAC-2025-005", "Diseño Creativo SA", "Diseño catálogo digital",     "2025-04-20", 1200, 21, 15, "pendiente")
        self.add_factura("FAC-2025-006", "Marketing Digital SL", "Consultoría SEO",             "2025-05-15",  900, 21, 15, "pendiente")

        self.add_gasto("Adobe Creative Cloud",    "software",   "2025-01-05",  57.64, 21, True)
        self.add_gasto("Material de oficina",     "oficina",    "2025-01-20",  45.00, 21, True)
        self.add_gasto("Curso marketing digital", "formacion",  "2025-02-12", 297.00, 21, True)
        self.add_gasto("Dominio y hosting",       "software",   "2025-02-28", 120.00, 21, True)
        self.add_gasto("Desplazamiento cliente",  "transporte", "2025-03-10",  35.00,  0, True)
        self.add_gasto("Seguro RC Profesional",   "seguro",     "2025-04-01", 400.00,  0, True)

    # ─────────────────────────────────────────────────────────
    # CIERRE DE CONEXIÓN
    # ─────────────────────────────────────────────────────────
    def close(self):
        self.conn.close()