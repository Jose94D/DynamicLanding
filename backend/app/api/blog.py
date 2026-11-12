"""Blog, mensajes de contacto y analíticas de visitas."""
import os

from fastapi import Depends, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models as m
from ..db import get_db
from ..schemas import AnaliticasOut, ArticuloIn, ArticuloOut, ArticuloResumen, MensajeOut, MensajesOut, Serie
from ..utils import generar_slug
from .comun import obtener_o_404, router_admin

router = router_admin('blog, mensajes y analíticas')


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


# ---------- Analíticas ----------
# Formatos de DATE_FORMAT (MySQL/MariaDB). %u = semana del año empezando en lunes, igual que el %W de SQLite.
FORMATO_ANIO, FORMATO_MES, FORMATO_SEMANA = '%Y', '%Y-%m', '%Y-%u'


def _serie(db, formato):
    periodo = func.date_format(m.AnaliticaVisita.fecha, formato)
    filas = db.execute(select(periodo, func.count()).group_by(periodo).order_by(periodo))
    return [Serie(periodo=p, total=t) for p, t in filas]


def _del_periodo_actual(db, formato):
    return db.scalar(select(func.count()).select_from(m.AnaliticaVisita).where(
        func.date_format(m.AnaliticaVisita.fecha, formato) == func.date_format(func.now(), formato)))


@router.get('/analiticas', response_model=AnaliticasOut)
def analiticas(db: Session = Depends(get_db)):
    return AnaliticasOut(
        total=db.scalar(select(func.count()).select_from(m.AnaliticaVisita)),
        anio_actual=_del_periodo_actual(db, FORMATO_ANIO),
        mes_actual=_del_periodo_actual(db, FORMATO_MES),
        semana_actual=_del_periodo_actual(db, FORMATO_SEMANA),
        por_anio=_serie(db, FORMATO_ANIO),
        por_mes=_serie(db, FORMATO_MES),
        por_semana=_serie(db, FORMATO_SEMANA),
    )
