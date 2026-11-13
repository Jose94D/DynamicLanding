"""Blog y mensajes de contacto."""
import os

from fastapi import Depends, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models as m
from ..db import get_db
from ..schemas import ArticuloIn, ArticuloOut, ArticuloResumen, MensajeOut, MensajesOut
from ..utils import generar_slug
from .comun import obtener_o_404, router_admin

router = router_admin('blog y mensajes')


# ---------- Blog ----------
@router.get('/blog', response_model=list[ArticuloResumen])
def listar_articulos(db: Session = Depends(get_db)):
    return db.scalars(select(m.ContenidoBlog).order_by(m.ContenidoBlog.fecha_publicacion.desc())).all()


@router.get('/blog/{id:int}', response_model=ArticuloOut)
def ver_articulo(id: int, db: Session = Depends(get_db)):
    return obtener_o_404(db, m.ContenidoBlog, id)


@router.post('/blog', response_model=ArticuloOut, status_code=201)
def crear_articulo(datos: ArticuloIn, db: Session = Depends(get_db)):
    slug = generar_slug(datos.titulo) or 'articulo'
    if db.scalar(select(m.ContenidoBlog.id).where(m.ContenidoBlog.slug == slug)):
        slug = f'{slug}-{os.urandom(2).hex()}'
    articulo = m.ContenidoBlog(**datos.model_dump(), slug=slug)
    db.add(articulo)
    db.commit()
    db.refresh(articulo)  # trae fecha_publicacion, que la pone el servidor
    return articulo


@router.put('/blog/{id:int}', response_model=ArticuloOut)
def editar_articulo(id: int, datos: ArticuloIn, db: Session = Depends(get_db)):
    articulo = obtener_o_404(db, m.ContenidoBlog, id)
    # El slug NO se regenera al editar: así no se rompen links ya compartidos.
    for campo, valor in datos.model_dump().items():
        setattr(articulo, campo, valor)
    db.commit()
    return articulo


@router.delete('/blog/{id:int}', status_code=204)
def eliminar_articulo(id: int, db: Session = Depends(get_db)):
    db.delete(obtener_o_404(db, m.ContenidoBlog, id))
    db.commit()
    return Response(status_code=204)


# ---------- Mensajes ----------
@router.get('/mensajes', response_model=MensajesOut)
def listar_mensajes(db: Session = Depends(get_db)):
    mensajes = db.scalars(select(m.MensajeContacto).order_by(m.MensajeContacto.fecha_envio.desc())).all()
    return MensajesOut(mensajes=mensajes, no_leidos=sum(not x.leido for x in mensajes))


@router.post('/mensajes/{id:int}/leido', response_model=MensajeOut)
def marcar_leido(id: int, db: Session = Depends(get_db)):
    mensaje = obtener_o_404(db, m.MensajeContacto, id)
    mensaje.leido = True
    db.commit()
    return mensaje


@router.delete('/mensajes/{id:int}', status_code=204)
def eliminar_mensaje(id: int, db: Session = Depends(get_db)):
    db.delete(obtener_o_404(db, m.MensajeContacto, id))
    db.commit()
    return Response(status_code=204)

