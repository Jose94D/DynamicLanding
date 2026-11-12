"""Módulos de la landing y contenido de una sola fila: hero, about, contacto, SEO y redes."""
from fastapi import Depends, File, Form, HTTPException, Response, UploadFile
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .. import imagenes
from .. import models as m
from ..db import get_db
from ..schemas import (AboutOut, ContactoIn, ContactoOut, Hero, ModuloEstado, ModuloOut, OrdenSlugs, RedIn, RedOut,
                       Seo, Visibilidad)
from ..social_api import invalidar_cache
from .comun import reordenar, router_admin

router = router_admin('contenido')

PLATAFORMAS_SOPORTADAS = ['instagram']


def _ordenados(db, modelo):
    return db.scalars(select(modelo).order_by(modelo.orden)).all()


# ---------- Módulos de la landing (dashboard) ----------
@router.get('/modulos', response_model=list[ModuloOut])
def listar_modulos(db: Session = Depends(get_db)):
    return _ordenados(db, m.Modulo)


@router.put('/modulos', response_model=list[ModuloOut], summary='Guarda visibilidad y orden de todos los módulos')
def guardar_modulos(estados: list[ModuloEstado], db: Session = Depends(get_db)):
    for estado in estados:
        db.execute(update(m.Modulo).where(m.Modulo.id == estado.id).values(activo=estado.activo, orden=estado.orden))
    db.commit()
    return _ordenados(db, m.Modulo)


# ---------- Hero ----------
@router.get('/hero', response_model=Hero)
def ver_hero(db: Session = Depends(get_db)):
    return db.get(m.ContenidoHero, 1)


@router.put('/hero', response_model=Hero)
def guardar_hero(datos: Hero, db: Session = Depends(get_db)):
    hero = db.get(m.ContenidoHero, 1)
    for campo, valor in datos.model_dump().items():
        setattr(hero, campo, valor)
    db.commit()
    return hero


# ---------- Sobre nosotros ----------
def _about(db):
    about = db.get(m.ContenidoAbout, 1)
    return AboutOut(titulo=about.titulo, descripcion=about.descripcion, mision=about.mision,
                    nombre_archivo=about.nombre_archivo, bloques=_ordenados(db, m.ContenidoAboutBloque))


@router.get('/about', response_model=AboutOut)
def ver_about(db: Session = Depends(get_db)):
    return _about(db)


@router.put('/about', response_model=AboutOut, summary='Textos e imagen opcional (multipart)')
def guardar_about(
    titulo: str = Form(min_length=1),
    descripcion: str = Form(''),
    mision: str = Form(''),
    imagen: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    about = db.get(m.ContenidoAbout, 1)
    # Reemplazar la imagen es opcional: sin archivo nuevo se conserva la actual.
    if imagen and imagen.filename:
        nuevo = imagenes.subir(imagen, 'about', imagenes.MAX_ANCHO_ABOUT)
        imagenes.eliminar('about', about.nombre_archivo)
        about.nombre_archivo = nuevo
    about.titulo, about.descripcion, about.mision = titulo.strip(), descripcion.strip(), mision.strip()
    db.commit()
    return _about(db)


@router.put('/about/bloques/orden', status_code=204)
def ordenar_bloques_about(datos: OrdenSlugs, db: Session = Depends(get_db)):
    reordenar(db, m.ContenidoAboutBloque, datos.orden)
    return Response(status_code=204)


@router.patch('/about/bloques/{id}', response_model=ModuloOut)
def visibilidad_bloque_about(id: str, datos: Visibilidad, db: Session = Depends(get_db)):
    bloque = db.get(m.ContenidoAboutBloque, id)
    if not bloque:
        raise HTTPException(404, 'El bloque no existe.')
    bloque.activo = datos.activo
    db.commit()
    return bloque


# ---------- Contáctanos ----------
def _contacto(db):
    return ContactoOut(datos=db.get(m.ContactDatos, 1), direccion=db.get(m.ContactMapa, 1).direccion,
                       submodulos=_ordenados(db, m.ContactSubmodulo))


@router.get('/contacto', response_model=ContactoOut)
def ver_contacto(db: Session = Depends(get_db)):
    return _contacto(db)


@router.put('/contacto', response_model=ContactoOut, summary='Datos, dirección del mapa y visibilidad de sub-módulos')
def guardar_contacto(datos: ContactoIn, db: Session = Depends(get_db)):
    fila = db.get(m.ContactDatos, 1)
    for campo, valor in datos.datos.model_dump().items():
        setattr(fila, campo, valor)
    db.get(m.ContactMapa, 1).direccion = datos.direccion
    for sub in datos.submodulos:
        db.execute(update(m.ContactSubmodulo).where(m.ContactSubmodulo.id == sub.id).values(activo=sub.activo))
    db.commit()
    return _contacto(db)


@router.put('/contacto/submodulos/orden', status_code=204)
def ordenar_submodulos_contacto(datos: OrdenSlugs, db: Session = Depends(get_db)):
    reordenar(db, m.ContactSubmodulo, datos.orden)
    return Response(status_code=204)


# ---------- SEO (landing y blog comparten forma y reglas) ----------
def _guardar_seo(db, modelo, datos):
    fila = db.get(modelo, 1)
    for campo, valor in datos.model_dump().items():
        setattr(fila, campo, valor)
    db.commit()
    return fila


@router.get('/seo', response_model=Seo)
def ver_seo(db: Session = Depends(get_db)):
    return db.get(m.ConfiguracionSeo, 1)


@router.put('/seo', response_model=Seo)
def guardar_seo(datos: Seo, db: Session = Depends(get_db)):
    return _guardar_seo(db, m.ConfiguracionSeo, datos)


@router.get('/seo/blog', response_model=Seo)
def ver_seo_blog(db: Session = Depends(get_db)):
    return db.get(m.ConfiguracionSeoBlog, 1)


@router.put('/seo/blog', response_model=Seo)
def guardar_seo_blog(datos: Seo, db: Session = Depends(get_db)):
    return _guardar_seo(db, m.ConfiguracionSeoBlog, datos)


# ---------- Redes sociales ----------
def _red_out(red):
    return RedOut(plataforma=red.plataforma, account_id=red.account_id, activo_api=red.activo_api,
                  tiene_token=bool(red.access_token))


@router.get('/redes', response_model=list[RedOut], summary='Una fila por plataforma soportada (aunque no esté configurada)')
def listar_redes(db: Session = Depends(get_db)):
    guardadas = {r.plataforma: r for r in db.scalars(select(m.ConfiguracionRedes))}
    return [_red_out(guardadas.get(p) or m.ConfiguracionRedes(plataforma=p, activo_api=False)) for p in PLATAFORMAS_SOPORTADAS]


@router.put('/redes/{plataforma}', response_model=RedOut)
def guardar_red(plataforma: str, datos: RedIn, db: Session = Depends(get_db)):
    if plataforma not in PLATAFORMAS_SOPORTADAS:
        raise HTTPException(404, 'Plataforma no soportada.')
    red = db.scalar(select(m.ConfiguracionRedes).where(m.ConfiguracionRedes.plataforma == plataforma))
    if red is None:
        red = m.ConfiguracionRedes(plataforma=plataforma)
        db.add(red)
    if datos.access_token is not None:
        red.access_token = datos.access_token
    red.account_id, red.activo_api = datos.account_id, datos.activo_api
    db.commit()
    invalidar_cache(datos.account_id)
    return _red_out(red)
