# Gestión de Pedidos — Backend FastAPI

Backend completo para gestión de clientes, productos, ingredientes, pedidos,
stock e inventario de un emprendimiento gastronómico.

---

## Requisitos

- Python 3.11+
- pip

---

## Instalación

```bash
# 1. Clonar / descomprimir el proyecto
cd proyecto

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
# El archivo .env ya viene con valores para desarrollo local (SQLite)
# Para producción, cambiar DATABASE_URL por una cadena de PostgreSQL:
# DATABASE_URL="postgresql://user:password@localhost:5432/emprendimiento"

# 5. Levantar el servidor
uvicorn main:app --reload
```

La API queda disponible en: **http://localhost:8000**
Documentación interactiva: **http://localhost:8000/docs**

---

## Estructura del proyecto

```
proyecto/
├── core/
│   ├── config.py               # Configuración y variables de entorno
│   ├── database.py             # Engine, sesión y Base declarativa
│   └── exceptions.py           # Excepciones de dominio
├── models/
│   ├── cliente.py
│   ├── producto.py
│   ├── ingrediente.py
│   ├── producto_ingrediente.py # Tabla de recetas
│   ├── pedido.py
│   ├── detalle_pedido.py
│   ├── compra.py
│   ├── detalle_compra.py
│   └── movimiento_stock.py     # Historial de stock (auditoría)
├── schemas/
│   ├── cliente_schema.py
│   ├── producto_schema.py
│   ├── ingrediente_schema.py
│   ├── pedido_schema.py
│   ├── compra_schema.py
│   ├── inventario_schema.py    # Validación stock, ajustes, compras sugeridas
│   └── finanzas_schema.py
├── repositories/               # Acceso a datos (solo queries, sin lógica)
│   ├── cliente_repository.py
│   ├── producto_repository.py
│   ├── ingrediente_repository.py
│   ├── pedido_repository.py
│   ├── compra_repository.py
│   └── movimiento_stock_repository.py
├── services/                   # Lógica de negocio
│   ├── cliente_service.py
│   ├── catalogo_service.py
│   ├── ingrediente_service.py
│   ├── pedido_service.py
│   ├── compra_service.py
│   ├── stock_service.py        # ← Servicio central de inventario
│   └── finanzas_service.py
├── routers/                    # Endpoints HTTP
│   ├── cliente_router.py
│   ├── catalogo_router.py
│   ├── ingrediente_router.py
│   ├── pedido_router.py
│   ├── compra_router.py
│   ├── inventario_router.py
│   └── finanzas_router.py
├── main.py                     # Entry point — app + exception handlers
├── requirements.txt
└── .env
```

---

## Endpoints principales

| Módulo | Base URL |
|---|---|
| Clientes | `/clientes` |
| Catálogo | `/productos` |
| Ingredientes | `/ingredientes` |
| Pedidos | `/pedidos` |
| Compras | `/compras` |
| Inventario | `/inventario` |
| Finanzas | `/finanzas` |

### Flujo de un pedido

```
POST /pedidos                     → Crear pedido (estado: PENDIENTE)
GET  /pedidos/{id}/validar-stock  → Verificar stock antes de avanzar
PATCH /pedidos/{id}/estado        → { "nuevo_estado": "EN_PROCESO" }
PATCH /pedidos/{id}/estado        → { "nuevo_estado": "COMPLETADO" }
  └── Consume stock automáticamente y registra movimientos
PATCH /pedidos/{id}/estado        → { "nuevo_estado": "CANCELADO" }
  └── Si venía de COMPLETADO, revierte el stock
```

### Compras sugeridas

```
GET /inventario/compras-sugeridas
→ Analiza todos los pedidos PENDIENTES y devuelve
  exactamente qué ingredientes comprar y en qué cantidad.
```

---

## Cambiar a PostgreSQL

Solo cambiar en `.env`:

```
DATABASE_URL="postgresql://usuario:contraseña@localhost:5432/emprendimiento"
```

No se requiere ningún otro cambio en el código.

---

## Migraciones con Alembic (opcional)

```bash
alembic init alembic
# Editar alembic.ini con la DATABASE_URL
# Editar alembic/env.py para importar Base desde core.database
alembic revision --autogenerate -m "initial"
alembic upgrade head
```
