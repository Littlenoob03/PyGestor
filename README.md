# PyGestor - Sistema de Gestión Financiera Multiplataforma

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/UI-Flet-792EE5.svg)](https://flet.dev/)
[![Database](https://img.shields.io/badge/Database-SQLite-003B57.svg)](https://www.sqlite.org/)
[![Analytics](https://img.shields.io/badge/Analytics-Matplotlib-11557C.svg)](https://matplotlib.org/)

**PyGestor** es una solución de escritorio multiplataforma orientada a la administración y análisis de finanzas personales. Centraliza el registro de flujos de caja (ingresos y gastos), la clasificación por centros de coste y la proyección analítica en tiempo real mediante un cuadro de mando con visualizaciones dinámicas integradas.

<p align="center">
  <img src="assets/dashboard.png" alt="Vista Principal del Dashboard de PyGestor" width="100%">
</p>

---

##  Características Principales

- **Control de Acceso y Autenticación:** Módulo de autenticación local que restringe el acceso al aplicativo y asegura el aislamiento de la información entre perfiles.
- **Cuadro de Mando Ejecutivo (Dashboard):** Visualización consolidada de métricas clave (ingresos acumulados, gastos totales y balance neto) junto a un histórico reciente de transacciones.
- **Gestión de Transacciones:**
  - **Ingresos:** Registro de entradas de capital con seguimiento de estado operativo (`Cobrado` / `Pendiente`) y atributos de origen, concepto y fecha.
  - **Gastos:** Clasificación sistemática de egresos por categorías predefinidas, con soporte completo para operaciones de edición y borrado.
- **Módulo de Analítica Financiera:**
  - Monitorización comparativa mensual de entradas frente a salidas de capital.
  - Distribución porcentual del consumo mediante diagramas de sectores.
  - Análisis agregado y tablas de rendimiento por trimestres fiscales (T1–T4).
- **Gestión de Configuración y Perfil:** Administración de preferencias de usuario, parámetros de cuenta y visualización de niveles de suscripción.
- **Arquitectura de Interfaz Adaptativa:** Diseño SPA (*Single Page Application*) construido con maquetación elástica para garantizar usabilidad en diversas resoluciones de pantalla.

---

##  Stack Tecnológico

- **Lenguaje de Programación:** Python 3.12
- **Capa de Presentación (UI):** Flet (entorno reactivo basado en Flutter)
- **Capa de Persistencia:** SQLite (motor relacional embebido para almacenamiento local seguro)
- **Motor Estadístico:** Matplotlib (procesamiento y vectorización gráfica en memoria mediante búfer de bytes)

---

##  Arquitectura del Repositorio

El proyecto implementa una separación estricta de responsabilidades:

```text
PyGestor/
├── assets/                     # Recursos estáticos de la interfaz
├── backend/
│   ├── database.py             # Capa de acceso a datos y abstracción relacional
│   ├── logic.py                # Lógica de negocio y motor de agregación contable
│   └── models.py               # Modelos de entidades de dominio
├── frontend/
│   ├── dashboard.py            # Vista principal del cuadro de mando
│   ├── formulario_gasto.py     # Componentes de entrada y edición de gastos
│   ├── formulario_ingreso.py   # Componentes de entrada y edición de ingresos
│   ├── gastos.py               # Vistas tabulares y filtrado de gastos
│   ├── graficos.py             # Generación en memoria de representaciones analíticas
│   ├── informes.py             # Panel de agregación y reportes trimestrales
│   ├── ingresos.py             # Vistas tabulares y conciliación de ingresos
│   ├── login.py                # Flujos de autenticación y alta de usuario
│   ├── perfil.py               # Panel de preferencias y configuración
│   └── styles.py               # Sistema de diseño, tokens cromáticos y componentes
├── .gitignore                  # Reglas de exclusión para Git
├── main.py                     # Punto de entrada y orquestador del ciclo de vida
├── README.md                   # Documentación principal del proyecto
└── requirements.txt            # Dependencias del entorno
```

> **Nota de configuración:** La base de datos local se inicializa automáticamente durante la primera ejecución de la aplicación si no se detecta el archivo `.db` en el directorio del proyecto.

---

## ️ Despliegue y Puesta en Marcha

### Requisitos Previos

- Python 3.10 o superior (recomendado Python 3.12).
- Gestor de paquetes `pip` y soporte para entornos virtuales `venv`.

### 1. Clonar el repositorio

```bash
git clone https://github.com/Littlenoob03/PyGestor.git
cd PyGestor
```

### 2. Configurar el entorno virtual

- **Linux / macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

- **Windows:**
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Ejecución del aplicativo

```bash
python main.py
```

---

##  Modelo Lógico de Datos

El diseño relacional garantiza la integridad referencial y el aislamiento de las operaciones:

- **Entidad `usuarios`:** Custodia los identificadores de cuenta, parámetros de acceso y metadatos de configuración del perfil.
- **Entidad `ingresos`:** Registra las transacciones positivas, asociando importes, conceptos y estados de cobro al identificador del usuario activo.
- **Entidad `gastos`:** Almacena los egresos económicos clasificados por categoría y fecha, vinculados de forma unívoca a la sesión activa mediante claves foráneas.

---

##  Hoja de Ruta (Roadmap)

- [ ] **Integración Bancaria (Open Banking):** Sincronización automática de movimientos financieros mediante conexiones directas a APIs bancarias homologadas.
- [ ] **Pasarela de Suscripciones:** Habilitación de pasarelas de pago externas para monetización de módulos avanzados.
- [ ] **Entornos Multiusuario y Presupuestos Compartidos:** Soporte para gestión de fondos colaborativos y balances consolidados entre múltiples usuarios.

---

##  Autoría y Créditos

- **Autor:** Lucas Ceprián Gallego
- **Proyecto Académico:** Trabajo de Fin de Grado (TFG)
- **Especialidad:** Desarrollo de Aplicaciones Multiplataforma (DAM)