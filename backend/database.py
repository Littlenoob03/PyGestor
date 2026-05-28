import sqlite3
import os
from typing import List, Optional
from backend.models import Ingreso, Gasto

DB_FILE = "pygestor.db"


class Database:
    def __init__(self):
        self.current_user_id = None
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

        # Add usuario_id columns to ingresos and gastos if they don't exist
        cur.execute("PRAGMA table_info(ingresos)")
        columns = [row[1] for row in cur.fetchall()]
        if "usuario_id" not in columns:
            cur.execute("ALTER TABLE ingresos ADD COLUMN usuario_id INTEGER NOT NULL DEFAULT 1")

        cur.execute("PRAGMA table_info(gastos)")
        columns = [row[1] for row in cur.fetchall()]
        if "usuario_id" not in columns:
            cur.execute("ALTER TABLE gastos ADD COLUMN usuario_id INTEGER NOT NULL DEFAULT 1")
            
        # Add new columns to usuarios if they don't exist
        cur.execute("PRAGMA table_info(usuarios)")
        user_cols = [row[1] for row in cur.fetchall()]
        if "email" not in user_cols:
            cur.execute("ALTER TABLE usuarios ADD COLUMN email TEXT DEFAULT ''")
        if "telefono" not in user_cols:
            cur.execute("ALTER TABLE usuarios ADD COLUMN telefono TEXT DEFAULT ''")
        if "foto" not in user_cols:
            cur.execute("ALTER TABLE usuarios ADD COLUMN foto TEXT DEFAULT ''")
        if "plan" not in user_cols:
            cur.execute("ALTER TABLE usuarios ADD COLUMN plan TEXT DEFAULT 'Plan Personal'")

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

    def get_usuario_by_id(self, id: int):
        row = self.conn.execute(
            "SELECT * FROM usuarios WHERE id = ?", (id,)
        ).fetchone()
        return dict(row) if row else None

    def get_usuario_by_username(self, username):
        row = self.conn.execute(
            "SELECT * FROM usuarios WHERE username = ?",
            (username,)
        ).fetchone()
        return dict(row) if row else None

    def add_usuario(self, username, password, email=''):
        try:
            self.conn.execute(
                "INSERT INTO usuarios (username, password, email, telefono, foto, plan) VALUES (?, ?, ?, '', '', 'Plan Personal')",
                (username, password, email)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # Usuario ya existe

    def update_usuario(self, id: int, **kwargs):
        allowed = {"username", "password", "email", "telefono", "foto", "plan"}
        fields  = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return self.get_usuario_by_id(id)
        sets = ", ".join(f"{k} = ?" for k in fields)
        self.conn.execute(
            f"UPDATE usuarios SET {sets} WHERE id = ?",
            (*fields.values(), id),
        )
        self.conn.commit()
        return self.get_usuario_by_id(id)

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
            usuario_id=row["usuario_id"] if "usuario_id" in row.keys() else 1,
        )

    def _row_to_gasto(self, row) -> Gasto:
        return Gasto(
            id=row["id"],
            descripcion=row["descripcion"],
            categoria=row["categoria"],
            fecha=row["fecha"],
            importe=row["importe"],
            usuario_id=row["usuario_id"] if "usuario_id" in row.keys() else 1,
        )

    # ─────────────────────────────────────────────────────────
    # INGRESOS — CRUD
    # ─────────────────────────────────────────────────────────
    def add_ingreso(self, origen, concepto, fecha, importe, estado="cobrado") -> Ingreso:
        cur = self.conn.cursor()
        uid = self.current_user_id if self.current_user_id is not None else -1
        cur.execute(
            "INSERT INTO ingresos "
            "(origen, concepto, fecha, importe, estado, usuario_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (origen, concepto, fecha, importe, estado, uid),
        )
        self.conn.commit()
        return self.get_ingreso(cur.lastrowid)

    def update_ingreso(self, id: int, **kwargs) -> Optional[Ingreso]:
        allowed = {"origen", "concepto", "fecha", "importe", "estado"}
        fields  = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return self.get_ingreso(id)
        sets = ", ".join(f"{k} = ?" for k in fields)
        uid = self.current_user_id if self.current_user_id is not None else -1
        self.conn.execute(
            f"UPDATE ingresos SET {sets} WHERE id = ? AND usuario_id = ?",
            (*fields.values(), id, uid),
        )
        self.conn.commit()
        return self.get_ingreso(id)

    def delete_ingreso(self, id: int):
        uid = self.current_user_id if self.current_user_id is not None else -1
        self.conn.execute("DELETE FROM ingresos WHERE id = ? AND usuario_id = ?", (id, uid))
        self.conn.commit()

    def get_ingreso(self, id: int) -> Optional[Ingreso]:
        uid = self.current_user_id if self.current_user_id is not None else -1
        row = self.conn.execute(
            "SELECT * FROM ingresos WHERE id = ? AND usuario_id = ?", (id, uid)
        ).fetchone()
        return self._row_to_ingreso(row) if row else None

    @property
    def ingresos(self) -> List[Ingreso]:
        uid = self.current_user_id if self.current_user_id is not None else -1
        rows = self.conn.execute(
            "SELECT * FROM ingresos WHERE usuario_id = ? ORDER BY fecha DESC", (uid,)
        ).fetchall()
        return [self._row_to_ingreso(r) for r in rows]

    def ingresos_by_year(self, year: int) -> List[Ingreso]:
        uid = self.current_user_id if self.current_user_id is not None else -1
        rows = self.conn.execute(
            "SELECT * FROM ingresos WHERE strftime('%Y', fecha) = ? AND usuario_id = ? ORDER BY fecha DESC",
            (str(year), uid),
        ).fetchall()
        return [self._row_to_ingreso(r) for r in rows]

    def ingresos_by_trimestre(self, year: int, t: int) -> List[Ingreso]:
        uid = self.current_user_id if self.current_user_id is not None else -1
        month_ranges = {1: ("01","03"), 2: ("04","06"),
                        3: ("07","09"), 4: ("10","12")}
        m_ini, m_fin = month_ranges[t]
        rows = self.conn.execute(
            "SELECT * FROM ingresos "
            "WHERE strftime('%Y', fecha) = ? "
            "  AND strftime('%m', fecha) BETWEEN ? AND ? "
            "  AND usuario_id = ? "
            "ORDER BY fecha DESC",
            (str(year), m_ini, m_fin, uid),
        ).fetchall()
        return [self._row_to_ingreso(r) for r in rows]

    # ─────────────────────────────────────────────────────────
    # GASTOS — CRUD
    # ─────────────────────────────────────────────────────────
    def add_gasto(self, descripcion, categoria, fecha, importe) -> Gasto:
        cur = self.conn.cursor()
        uid = self.current_user_id if self.current_user_id is not None else -1
        cur.execute(
            "INSERT INTO gastos (descripcion, categoria, fecha, importe, usuario_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (descripcion, categoria, fecha, importe, uid),
        )
        self.conn.commit()
        return self.get_gasto(cur.lastrowid)

    def update_gasto(self, id: int, **kwargs) -> Optional[Gasto]:
        allowed = {"descripcion", "categoria", "fecha", "importe"}
        fields  = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return self.get_gasto(id)
        sets = ", ".join(f"{k} = ?" for k in fields)
        uid = self.current_user_id if self.current_user_id is not None else -1
        self.conn.execute(
            f"UPDATE gastos SET {sets} WHERE id = ? AND usuario_id = ?",
            (*fields.values(), id, uid),
        )
        self.conn.commit()
        return self.get_gasto(id)

    def delete_gasto(self, id: int):
        uid = self.current_user_id if self.current_user_id is not None else -1
        self.conn.execute("DELETE FROM gastos WHERE id = ? AND usuario_id = ?", (id, uid))
        self.conn.commit()

    def get_gasto(self, id: int) -> Optional[Gasto]:
        uid = self.current_user_id if self.current_user_id is not None else -1
        row = self.conn.execute(
            "SELECT * FROM gastos WHERE id = ? AND usuario_id = ?", (id, uid)
        ).fetchone()
        return self._row_to_gasto(row) if row else None

    @property
    def gastos(self) -> List[Gasto]:
        uid = self.current_user_id if self.current_user_id is not None else -1
        rows = self.conn.execute(
            "SELECT * FROM gastos WHERE usuario_id = ? ORDER BY fecha DESC", (uid,)
        ).fetchall()
        return [self._row_to_gasto(r) for r in rows]

    def gastos_by_year(self, year: int) -> List[Gasto]:
        uid = self.current_user_id if self.current_user_id is not None else -1
        rows = self.conn.execute(
            "SELECT * FROM gastos WHERE strftime('%Y', fecha) = ? AND usuario_id = ? ORDER BY fecha DESC",
            (str(year), uid),
        ).fetchall()
        return [self._row_to_gasto(r) for r in rows]

    def gastos_by_trimestre(self, year: int, t: int) -> List[Gasto]:
        uid = self.current_user_id if self.current_user_id is not None else -1
        month_ranges = {1: ("01","03"), 2: ("04","06"),
                        3: ("07","09"), 4: ("10","12")}
        m_ini, m_fin = month_ranges[t]
        rows = self.conn.execute(
            "SELECT * FROM gastos "
            "WHERE strftime('%Y', fecha) = ? "
            "  AND strftime('%m', fecha) BETWEEN ? AND ? "
            "  AND usuario_id = ? "
            "ORDER BY fecha DESC",
            (str(year), m_ini, m_fin, uid),
        ).fetchall()
        return [self._row_to_gasto(r) for r in rows]

    # ─────────────────────────────────────────────────────────
    # DATOS DE DEMO (ELIMINADOS)
    # ─────────────────────────────────────────────────────────
    def seed_demo_data(self):
        # Insert admin user if empty
        if not self.conn.execute("SELECT 1 FROM usuarios LIMIT 1").fetchone():
            self.add_usuario("admin", "admin")
        
        # Ya no se insertan datos de prueba falsos.

    # ─────────────────────────────────────────────────────────
    # CIERRE DE CONEXIÓN
    # ─────────────────────────────────────────────────────────
    def close(self):
        self.conn.close()