"""
Copia todos los datos del database.db (SQLite, app Flask) a MySQL/MariaDB, conservando los ids.

Orden de uso (desde backend/):
    alembic upgrade head                                   # crea las tablas vacías
    python scripts/migrar_desde_sqlite.py ../database.db   # copia los datos
    python -m app.seed                                     # completa lo que falte

Se niega a correr si alguna tabla destino ya tiene datos, para no duplicar ni mezclar.
"""
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import func, select  # noqa: E402

from app.db import Base, engine  # noqa: E402
from app import models  # noqa: E402,F401  (registra las tablas)


def migrar(ruta_sqlite):
    origen = sqlite3.connect(ruta_sqlite)
    origen.row_factory = sqlite3.Row
    tablas_origen = {f[0] for f in origen.execute("SELECT name FROM sqlite_master WHERE type='table'")}

    with engine.begin() as destino:
        ocupadas = [t.name for t in Base.metadata.sorted_tables
                    if destino.execute(select(func.count()).select_from(t)).scalar()]
        if ocupadas:
            sys.exit(f'Abortado: estas tablas ya tienen datos en MySQL: {", ".join(ocupadas)}')

        for tabla in Base.metadata.sorted_tables:
            if tabla.name not in tablas_origen:
                print(f'  - {tabla.name}: no existe en SQLite, se omite')
                continue
            columnas = set(tabla.columns.keys())
            # Solo columnas que existen en ambos lados (bases SQLite viejas pueden no tener todas).
            filas = [{k: fila[k] for k in fila.keys() if k in columnas}
                     for fila in origen.execute(f'SELECT * FROM "{tabla.name}"')]
            if filas:
                destino.execute(tabla.insert(), filas)
            print(f'  ✓ {tabla.name}: {len(filas)} filas')

    origen.close()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit('Uso: python scripts/migrar_desde_sqlite.py <ruta a database.db>')
    migrar(sys.argv[1])
    print('Migración terminada. Ahora ejecuta: python -m app.seed')
