from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from core.config import get_settings

settings = get_settings()

# Para SQLite se necesita este argumento; para Postgres se elimina
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    pass


def get_db():
    """
    Dependencia inyectable para FastAPI.
    Abre una sesión, la cede al endpoint y la cierra al terminar.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Crea todas las tablas definidas en los modelos.
    Se llama una sola vez al arrancar la aplicación.
    """
    from models import cliente, producto, ingrediente, producto_ingrediente  # noqa
    from models import pedido, detalle_pedido, compra, detalle_compra, movimiento_stock  # noqa
    Base.metadata.create_all(bind=engine)
