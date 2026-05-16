import sqlite3
import os
from typing import List, Optional
from backend.models import Ingreso, Gasto

DB_FILE = "pygestor.db"


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
            CREATE TABLE IF NOT EXISTS ingresos (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                origen       TEXT    NOT NULL,
                concepto     TEXT    NOT NULL,
                fecha        TEXT    NOT NULL,
                importe      REAL    NOT NULL,
                estado       TEXT    NOT NULL DEFAULT 'cobrado'
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT    NOT NULL,
                categoria   TEXT    NOT NULL,
                fecha       TEXT    NOT NULL,
                importe     REAL    NOT NULL
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
    def _row_to_ingreso(self, row) -> Ingreso:
        return Ingreso(
            id=row["id"],
            origen=row["origen"],
            concepto=row["concepto"],
            fecha=row["fecha"],
            importe=row["importe"],
            estado=row["estado"],
        )

    def _row_to_gasto(self, row) -> Gasto:
        return Gasto(
            id=row["id"],
            descripcion=row["descripcion"],
            categoria=row["categoria"],
            fecha=row["fecha"],
            importe=row["importe"],
        )

    # ─────────────────────────────────────────────────────────
    # INGRESOS — CRUD
    # ─────────────────────────────────────────────────────────
    def add_ingreso(self, origen, concepto, fecha, importe, estado="cobrado") -> Ingreso:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO ingresos "
            "(origen, concepto, fecha, importe, estado) "
            "VALUES (?, ?, ?, ?, ?)",
            (origen, concepto, fecha, importe, estado),
        )
        self.conn.commit()
        return self.get_ingreso(cur.lastrowid)

    def update_ingreso(self, id: int, **kwargs) -> Optional[Ingreso]:
        allowed = {"origen", "concepto", "fecha", "importe", "estado"}
        fields  = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return self.get_ingreso(id)
        sets = ", ".join(f"{k} = ?" for k in fields)
        self.conn.execute(
            f"UPDATE ingresos SET {sets} WHERE id = ?",
            (*fields.values(), id),
        )
        self.conn.commit()
        return self.get_ingreso(id)

    def delete_ingreso(self, id: int):
        self.conn.execute("DELETE FROM ingresos WHERE id = ?", (id,))
        self.conn.commit()

    def get_ingreso(self, id: int) -> Optional[Ingreso]:
        row = self.conn.execute(
            "SELECT * FROM ingresos WHERE id = ?", (id,)
        ).fetchone()
        return self._row_to_ingreso(row) if row else None

    @property
    def ingresos(self) -> List[Ingreso]:
        rows = self.conn.execute(
            "SELECT * FROM ingresos ORDER BY fecha DESC"
        ).fetchall()
        return [self._row_to_ingreso(r) for r in rows]

    def ingresos_by_year(self, year: int) -> List[Ingreso]:
        rows = self.conn.execute(
            "SELECT * FROM ingresos WHERE strftime('%Y', fecha) = ? ORDER BY fecha DESC",
            (str(year),),
        ).fetchall()
        return [self._row_to_ingreso(r) for r in rows]

    def ingresos_by_trimestre(self, year: int, t: int) -> List[Ingreso]:
        month_ranges = {1: ("01","03"), 2: ("04","06"),
                        3: ("07","09"), 4: ("10","12")}
        m_ini, m_fin = month_ranges[t]
        rows = self.conn.execute(
            "SELECT * FROM ingresos "
            "WHERE strftime('%Y', fecha) = ? "
            "  AND strftime('%m', fecha) BETWEEN ? AND ? "
            "ORDER BY fecha DESC",
            (str(year), m_ini, m_fin),
        ).fetchall()
        return [self._row_to_ingreso(r) for r in rows]

    # ─────────────────────────────────────────────────────────
    # GASTOS — CRUD
    # ─────────────────────────────────────────────────────────
    def add_gasto(self, descripcion, categoria, fecha, importe) -> Gasto:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO gastos (descripcion, categoria, fecha, importe) "
            "VALUES (?, ?, ?, ?)",
            (descripcion, categoria, fecha, importe),
        )
        self.conn.commit()
        return self.get_gasto(cur.lastrowid)

    def update_gasto(self, id: int, **kwargs) -> Optional[Gasto]:
        allowed = {"descripcion", "categoria", "fecha", "importe"}
        fields  = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return self.get_gasto(id)
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

        # Solo inserta si la tabla ingresos está vacía
        if self.ingresos:
            return

        self.add_ingreso("Empresa Principal SA", "Nómina Enero", "2025-01-28", 2500, "cobrado")
        self.add_ingreso("Venta Wallapop", "Bicicleta antigua", "2025-02-10",  150, "cobrado")
        self.add_ingreso("Empresa Principal SA", "Nómina Febrero", "2025-02-28", 2500, "cobrado")
        self.add_ingreso("Bizum", "Cena amigos", "2025-03-05",  45, "cobrado")
        self.add_ingreso("Empresa Principal SA", "Nómina Marzo", "2025-03-28", 2500, "cobrado")
        self.add_ingreso("Hacienda", "Devolución Renta", "2025-04-20", 350, "pendiente")

        self.add_gasto("Mercadona",    "alimentacion", "2025-01-05",  85.50)
        self.add_gasto("Netflix",      "ocio",         "2025-01-20",  15.99)
        self.add_gasto("Gimnasio",     "salud",        "2025-02-01",  45.00)
        self.add_gasto("Mercadona",    "alimentacion", "2025-02-12",  92.30)
        self.add_gasto("Restaurante",  "ocio",         "2025-03-10",  42.00)
        self.add_gasto("Seguro Coche", "vehiculo",     "2025-04-01", 350.00)

    # ─────────────────────────────────────────────────────────
    # CIERRE DE CONEXIÓN
    # ─────────────────────────────────────────────────────────
    def close(self):
        self.conn.close()