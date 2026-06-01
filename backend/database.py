import sqlite3
import os
from typing import List, Optional
from backend.models import Ingreso, Gasto

DB_FILE = "pygestor.db"


class Database:
    def __init__(self):
        self.current_user_id = None
        self.conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._crear_tablas()

    #TABLAS
    def _crear_tablas(self):
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

        cur.execute("PRAGMA table_info(ingresos)")
        columns = [row[1] for row in cur.fetchall()]
        if "usuario_id" not in columns:
            cur.execute("ALTER TABLE ingresos ADD COLUMN usuario_id INTEGER NOT NULL DEFAULT 1")

        cur.execute("PRAGMA table_info(gastos)")
        columns = [row[1] for row in cur.fetchall()]
        if "usuario_id" not in columns:
            cur.execute("ALTER TABLE gastos ADD COLUMN usuario_id INTEGER NOT NULL DEFAULT 1")
            
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


    # AUTENTICACIÓN DE USUARIOS
    def get_usser(self, username, password):
        """Busca un usuario por nombre y contraseña. Usado para iniciar sesión."""
        row = self.conn.execute(
            "SELECT * FROM usuarios WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        return dict(row) if row else None

    def get_usser_by_id(self, id: int):
        """Devuelve los datos de un usuario buscando por su ID interno."""
        row = self.conn.execute(
            "SELECT * FROM usuarios WHERE id = ?", (id,)
        ).fetchone()
        return dict(row) if row else None

    def get_usser_by_username(self, username):
        """Comprueba si existe un usuario con un nombre concreto, por ejemplo al registrar."""
        row = self.conn.execute(
            "SELECT * FROM usuarios WHERE username = ?",
            (username,)
        ).fetchone()
        return dict(row) if row else None

    def añadir_usuario(self, username, password, email=''):
        """Crea un nuevo usuario en la base de datos con los datos básicos."""
        try:
            self.conn.execute(
                "INSERT INTO usuarios (username, password, email, telefono, foto, plan) VALUES (?, ?, ?, '', '', 'Plan Personal')",
                (username, password, email)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def actualizar_usuario(self, id: int, **kwargs):
        """Actualiza los campos permitidos del perfil de un usuario (email, teléfono, foto...)."""
        allowed = {"username", "password", "email", "telefono", "foto", "plan"}
        fields  = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return self.get_usser_by_id(id)
        sets = ", ".join(f"{k} = ?" for k in fields)
        self.conn.execute(
            f"UPDATE usuarios SET {sets} WHERE id = ?",
            (*fields.values(), id),
        )
        self.conn.commit()
        return self.get_usser_by_id(id)

    # HELPERS
    def _fila_a_ingreso(self, row) -> Ingreso:
        """Convierte una fila de la tabla ingresos de la base de datos a un objeto Python 'Ingreso'."""
        return Ingreso(
            id=row["id"],
            origen=row["origen"],
            concepto=row["concepto"],
            fecha=row["fecha"],
            importe=row["importe"],
            estado=row["estado"],
            usuario_id=row["usuario_id"] if "usuario_id" in row.keys() else 1,
        )

    def _fila_a_gasto(self, row) -> Gasto:
        """Convierte una fila de la tabla gastos de la base de datos a un objeto Python 'Gasto'."""
        return Gasto(
            id=row["id"],
            descripcion=row["descripcion"],
            categoria=row["categoria"],
            fecha=row["fecha"],
            importe=row["importe"],
            usuario_id=row["usuario_id"] if "usuario_id" in row.keys() else 1,
        )


    # INGRESOS
    def añadir_ingreso(self, origen, concepto, fecha, importe, estado="cobrado") -> Ingreso:
        """Añade un nuevo ingreso asociado al usuario actual en la base de datos."""
        cur = self.conn.cursor()
        uid = self.current_user_id if self.current_user_id is not None else -1
        cur.execute(
            "INSERT INTO ingresos "
            "(origen, concepto, fecha, importe, estado, usuario_id) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (origen, concepto, fecha, importe, estado, uid),
        )
        self.conn.commit()
        return self.obtener_ingreso(cur.lastrowid)

    def actualizar_ingreso(self, id: int, **kwargs) -> Optional[Ingreso]:
        """Actualiza los datos de un ingreso existente, como cambiar su estado o importe."""
        allowed = {"origen", "concepto", "fecha", "importe", "estado"}
        fields  = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return self.obtener_ingreso(id)
        sets = ", ".join(f"{k} = ?" for k in fields)
        uid = self.current_user_id if self.current_user_id is not None else -1
        self.conn.execute(
            f"UPDATE ingresos SET {sets} WHERE id = ? AND usuario_id = ?",
            (*fields.values(), id, uid),
        )
        self.conn.commit()
        return self.obtener_ingreso(id)

    def eliminar_ingreso(self, id: int):
        """Elimina un ingreso de la base de datos de forma permanente."""
        uid = self.current_user_id if self.current_user_id is not None else -1
        self.conn.execute("DELETE FROM ingresos WHERE id = ? AND usuario_id = ?", (id, uid))
        self.conn.commit()

    def obtener_ingreso(self, id: int) -> Optional[Ingreso]:
        """Obtiene la información detallada de un solo ingreso por su ID."""
        uid = self.current_user_id if self.current_user_id is not None else -1
        row = self.conn.execute(
            "SELECT * FROM ingresos WHERE id = ? AND usuario_id = ?", (id, uid)
        ).fetchone()
        return self._fila_a_ingreso(row) if row else None

    @property
    def ingresos(self) -> List[Ingreso]:
        """Devuelve todos los ingresos del usuario actual ordenados desde el más reciente."""
        uid = self.current_user_id if self.current_user_id is not None else -1
        rows = self.conn.execute(
            "SELECT * FROM ingresos WHERE usuario_id = ? ORDER BY fecha DESC", (uid,)
        ).fetchall()
        return [self._fila_a_ingreso(r) for r in rows]

    def ingresos_por_año(self, year: int) -> List[Ingreso]:
        """Devuelve los ingresos que pertenecen a un año específico."""
        uid = self.current_user_id if self.current_user_id is not None else -1
        rows = self.conn.execute(
            "SELECT * FROM ingresos WHERE strftime('%Y', fecha) = ? AND usuario_id = ? ORDER BY fecha DESC",
            (str(year), uid),
        ).fetchall()
        return [self._fila_a_ingreso(r) for r in rows]

    def ingresos_por_trimestre(self, year: int, t: int) -> List[Ingreso]:
        """Filtra y devuelve los ingresos correspondientes a un trimestre de un año concreto."""
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
        return [self._fila_a_ingreso(r) for r in rows]


    # GASTOS
    def añadir_gasto(self, descripcion, categoria, fecha, importe) -> Gasto:
        """Registra un nuevo gasto para el usuario actual."""
        cur = self.conn.cursor()
        uid = self.current_user_id if self.current_user_id is not None else -1
        cur.execute(
            "INSERT INTO gastos (descripcion, categoria, fecha, importe, usuario_id) "
            "VALUES (?, ?, ?, ?, ?)",
            (descripcion, categoria, fecha, importe, uid),
        )
        self.conn.commit()
        return self.obtener_gasto(cur.lastrowid)

    def actualizar_gasto(self, id: int, **kwargs) -> Optional[Gasto]:
        """Modifica los detalles de un gasto existente."""
        allowed = {"descripcion", "categoria", "fecha", "importe"}
        fields  = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return self.obtener_gasto(id)
        sets = ", ".join(f"{k} = ?" for k in fields)
        uid = self.current_user_id if self.current_user_id is not None else -1
        self.conn.execute(
            f"UPDATE gastos SET {sets} WHERE id = ? AND usuario_id = ?",
            (*fields.values(), id, uid),
        )
        self.conn.commit()
        return self.obtener_gasto(id)

    def eliminar_gasto(self, id: int):
        """Elimina de forma permanente un registro de gasto."""
        uid = self.current_user_id if self.current_user_id is not None else -1
        self.conn.execute("DELETE FROM gastos WHERE id = ? AND usuario_id = ?", (id, uid))
        self.conn.commit()

    def obtener_gasto(self, id: int) -> Optional[Gasto]:
        """Obtiene la información de un gasto individual usando su ID."""
        uid = self.current_user_id if self.current_user_id is not None else -1
        row = self.conn.execute(
            "SELECT * FROM gastos WHERE id = ? AND usuario_id = ?", (id, uid)
        ).fetchone()
        return self._fila_a_gasto(row) if row else None

    @property
    def gastos(self) -> List[Gasto]:
        """Lista todos los gastos del usuario ordenados por fecha."""
        uid = self.current_user_id if self.current_user_id is not None else -1
        rows = self.conn.execute(
            "SELECT * FROM gastos WHERE usuario_id = ? ORDER BY fecha DESC", (uid,)
        ).fetchall()
        return [self._fila_a_gasto(r) for r in rows]

    def gastos_por_año(self, year: int) -> List[Gasto]:
        """Devuelve únicamente los gastos de un año seleccionado."""
        uid = self.current_user_id if self.current_user_id is not None else -1
        rows = self.conn.execute(
            "SELECT * FROM gastos WHERE strftime('%Y', fecha) = ? AND usuario_id = ? ORDER BY fecha DESC",
            (str(year), uid),
        ).fetchall()
        return [self._fila_a_gasto(r) for r in rows]

    def gastos_por_trimestre(self, year: int, t: int) -> List[Gasto]:
        """Devuelve los gastos realizados en uno de los cuatro trimestres del año indicado."""
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
        return [self._fila_a_gasto(r) for r in rows]


    # CUENTA ADMIN (PRUEBAS)
    def cuenta_admin(self):
        """Crea una cuenta de administrador de demostración si la base de datos está vacía."""
        if not self.conn.execute("SELECT 1 FROM usuarios LIMIT 1").fetchone():
            self.añadir_usuario("admin", "admin")

    # CIERRE DE CONEXIÓN
    def cerrar_conexion(self):
        """Cierra la conexión con la base de datos SQLite de forma segura."""
        self.conn.cerrar_conexion()