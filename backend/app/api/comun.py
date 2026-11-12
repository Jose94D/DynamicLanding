from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update

from ..web import verificar_csrf
from .auth import admin_actual


def router_admin(tag: str) -> APIRouter:
    """Router bajo /api/admin que exige sesión de admin y token CSRF en todo lo que modifica datos."""
    return APIRouter(prefix='/api/admin', tags=[tag], dependencies=[Depends(admin_actual), Depends(verificar_csrf)])


def obtener_o_404(db, modelo, id_):
    fila = db.get(modelo, id_)
    if fila is None:
        raise HTTPException(404, 'El elemento no existe.')
    return fila


def siguiente_orden(db, modelo) -> int:
    """Los elementos nuevos van al final; el orden luego se ajusta arrastrando."""
    return db.scalar(select(func.coalesce(func.max(modelo.orden), 0))) + 1


def reordenar(db, modelo, ids):
    for posicion, id_ in enumerate(ids, start=1):
        db.execute(update(modelo).where(modelo.id == id_).values(orden=posicion))
    db.commit()
