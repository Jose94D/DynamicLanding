"""Listas ordenables: carrusel, galería, servicios y testimonios."""
from fastapi import Depends, File, Form, Response, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import imagenes
from .. import models as m
from ..db import get_db
from ..schemas import GaleriaOut, ImagenOut, Orden, ServicioIn, ServicioOut, TestimonioOut
from .comun import obtener_o_404, reordenar, router_admin, siguiente_orden

router = router_admin('listas')


def _ordenados(db, modelo):
    return db.scalars(select(modelo).order_by(modelo.orden)).all()


# ---------- Carrusel ----------
@router.get('/carrusel', response_model=list[ImagenOut])
def listar_carrusel(db: Session = Depends(get_db)):
    return _ordenados(db, m.ContenidoCarousel)


@router.post('/carrusel', response_model=ImagenOut, status_code=201)
def subir_carrusel(imagen: UploadFile = File(), db: Session = Depends(get_db)):
    fila = m.ContenidoCarousel(nombre_archivo=imagenes.subir(imagen, 'carousel', imagenes.MAX_ANCHO_CAROUSEL),
                               orden=siguiente_orden(db, m.ContenidoCarousel))
    db.add(fila)
    db.commit()
    return fila


@router.delete('/carrusel/{id:int}', status_code=204)
def eliminar_carrusel(id: int, db: Session = Depends(get_db)):
    fila = obtener_o_404(db, m.ContenidoCarousel, id)
    imagenes.eliminar('carousel', fila.nombre_archivo)
    db.delete(fila)
    db.commit()
    return Response(status_code=204)


@router.put('/carrusel/orden', status_code=204)
def ordenar_carrusel(datos: Orden, db: Session = Depends(get_db)):
    reordenar(db, m.ContenidoCarousel, datos.orden)
    return Response(status_code=204)


# ---------- Galería ----------
@router.get('/galeria', response_model=list[GaleriaOut])
def listar_galeria(db: Session = Depends(get_db)):
    return _ordenados(db, m.ContenidoGallery)


@router.post('/galeria', response_model=GaleriaOut, status_code=201)
def subir_galeria(imagen: UploadFile = File(), titulo: str = Form(''), db: Session = Depends(get_db)):
    fila = m.ContenidoGallery(nombre_archivo=imagenes.subir(imagen, 'gallery', imagenes.MAX_ANCHO_GALLERY),
                              titulo=titulo.strip(), orden=siguiente_orden(db, m.ContenidoGallery))
    db.add(fila)
    db.commit()
    return fila


@router.put('/galeria/{id:int}', response_model=GaleriaOut, summary='Cambia el título y, opcionalmente, la imagen')
def editar_galeria(id: int, titulo: str = Form(''), imagen: UploadFile | None = File(None), db: Session = Depends(get_db)):
    fila = obtener_o_404(db, m.ContenidoGallery, id)
    if imagen and imagen.filename:
        nuevo = imagenes.subir(imagen, 'gallery', imagenes.MAX_ANCHO_GALLERY)
        imagenes.eliminar('gallery', fila.nombre_archivo)
        fila.nombre_archivo = nuevo
    fila.titulo = titulo.strip()
    db.commit()
    return fila


@router.delete('/galeria/{id:int}', status_code=204)
def eliminar_galeria(id: int, db: Session = Depends(get_db)):
    fila = obtener_o_404(db, m.ContenidoGallery, id)
    imagenes.eliminar('gallery', fila.nombre_archivo)
    db.delete(fila)
    db.commit()
    return Response(status_code=204)


@router.put('/galeria/orden', status_code=204)
def ordenar_galeria(datos: Orden, db: Session = Depends(get_db)):
    reordenar(db, m.ContenidoGallery, datos.orden)
    return Response(status_code=204)


# ---------- Servicios ----------
@router.get('/servicios', response_model=list[ServicioOut])
def listar_servicios(db: Session = Depends(get_db)):
    return _ordenados(db, m.ContenidoService)


@router.post('/servicios', response_model=ServicioOut, status_code=201)
def crear_servicio(datos: ServicioIn, db: Session = Depends(get_db)):
    fila = m.ContenidoService(**datos.model_dump(), orden=siguiente_orden(db, m.ContenidoService))
    db.add(fila)
    db.commit()
    return fila


@router.put('/servicios/{id:int}', response_model=ServicioOut)
def editar_servicio(id: int, datos: ServicioIn, db: Session = Depends(get_db)):
    fila = obtener_o_404(db, m.ContenidoService, id)
    for campo, valor in datos.model_dump().items():
        setattr(fila, campo, valor)
    db.commit()
    return fila


@router.delete('/servicios/{id:int}', status_code=204)
def eliminar_servicio(id: int, db: Session = Depends(get_db)):
    db.delete(obtener_o_404(db, m.ContenidoService, id))
    db.commit()
    return Response(status_code=204)


@router.put('/servicios/orden', status_code=204)
def ordenar_servicios(datos: Orden, db: Session = Depends(get_db)):
    reordenar(db, m.ContenidoService, datos.orden)
    return Response(status_code=204)


# ---------- Testimonios ----------
@router.get('/testimonios', response_model=list[TestimonioOut])
def listar_testimonios(db: Session = Depends(get_db)):
    return _ordenados(db, m.ContenidoTestimonial)


@router.post('/testimonios', response_model=TestimonioOut, status_code=201)
def crear_testimonio(
    nombre: str = Form(min_length=1),
    texto: str = Form(min_length=1),
    cargo: str = Form(''),
    calificacion: int = Form(5, ge=1, le=5),
    foto: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    nombre_foto = imagenes.subir(foto, 'testimonials', imagenes.MAX_ANCHO_TESTIMONIAL) if foto and foto.filename else None
    fila = m.ContenidoTestimonial(nombre=nombre.strip(), cargo=cargo.strip(), texto=texto.strip(), foto=nombre_foto,
                                  calificacion=calificacion, orden=siguiente_orden(db, m.ContenidoTestimonial))
    db.add(fila)
    db.commit()
    return fila


@router.delete('/testimonios/{id:int}', status_code=204)
def eliminar_testimonio(id: int, db: Session = Depends(get_db)):
    fila = obtener_o_404(db, m.ContenidoTestimonial, id)
    imagenes.eliminar('testimonials', fila.foto)
    db.delete(fila)
    db.commit()
    return Response(status_code=204)


@router.put('/testimonios/orden', status_code=204)
def ordenar_testimonios(datos: Orden, db: Session = Depends(get_db)):
    reordenar(db, m.ContenidoTestimonial, datos.orden)
    return Response(status_code=204)
