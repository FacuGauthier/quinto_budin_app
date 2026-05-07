from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from core.config import get_settings
from core.database import create_tables
from core.exceptions import (
    RecursoNoEncontrado,
    RecursoInactivo,
    StockInsuficiente,
    TransicionEstadoInvalida,
    OperacionNoPermitida,
)
from routers import (
    cliente_router,
    catalogo_router,
    ingrediente_router,
    pedido_router,
    compra_router,
    inventario_router,
    finanzas_router,
)

settings = get_settings()

# ── EVENTOS DE INICIO ─────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    print(f"✅ {settings.APP_NAME} iniciado — DB: {settings.DATABASE_URL}")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Backend para gestión de pedidos, stock de ingredientes y finanzas "
        "de un emprendimiento gastronómico."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # En producción: lista tu dominio frontend aquí
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── MANEJADORES DE EXCEPCIONES DE DOMINIO ─────────────────────────────────────

@app.exception_handler(RecursoNoEncontrado)
async def recurso_no_encontrado_handler(_request: Request, exc: RecursoNoEncontrado):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc), "recurso": exc.recurso, "id": exc.id},
    )


@app.exception_handler(RecursoInactivo)
async def recurso_inactivo_handler(request: Request, exc: RecursoInactivo):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc), "recurso": exc.recurso, "id": exc.id},
    )


@app.exception_handler(StockInsuficiente)
async def stock_insuficiente_handler(request: Request, exc: StockInsuficiente):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": str(exc), "ingredientes_faltantes": exc.detalle},
    )


@app.exception_handler(TransicionEstadoInvalida)
async def transicion_invalida_handler(request: Request, exc: TransicionEstadoInvalida):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": str(exc),
            "estado_actual": exc.estado_actual,
            "estado_solicitado": exc.estado_nuevo,
        },
    )


@app.exception_handler(OperacionNoPermitida)
async def operacion_no_permitida_handler(request: Request, exc: OperacionNoPermitida):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"detail": exc.mensaje},
    )


# ── ROUTERS ───────────────────────────────────────────────────────────────────

app.include_router(cliente_router.router)
app.include_router(catalogo_router.router)
app.include_router(ingrediente_router.router)
app.include_router(pedido_router.router)
app.include_router(compra_router.router)
app.include_router(inventario_router.router)
app.include_router(finanzas_router.router)




# ── HEALTH CHECK ──────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0"}
