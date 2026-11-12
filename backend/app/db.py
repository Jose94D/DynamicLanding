from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import DATABASE_URL

# pool_recycle: MySQL en hosting compartido corta conexiones inactivas (wait_timeout);
# reciclarlas antes evita el error "MySQL server has gone away".
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=280)
SessionLocal = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Dependencia de FastAPI: una sesión por request, cerrada siempre al terminar."""
    with SessionLocal() as db:
        yield db
