import re

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models as m
from .db import get_db
from .web import flash, templates, verificar_csrf

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril', 5: 'Mayo', 6: 'Junio', 7: 'Julio',
    8: 'Agosto', 9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre',
}


def registrar_visita(request: Request, db: Session = Depends(get_db)):
    """Registra cada visita a una página pública (para el módulo de Analíticas)."""
    db.add(m.AnaliticaVisita(ruta=request.url.path))
    db.commit()


router = APIRouter(dependencies=[Depends(registrar_visita)], include_in_schema=False)  # páginas HTML, no API


def _todos(db, modelo, *orden):
    return db.scalars(select(modelo).order_by(*orden)).all()


def _articulos_publicados(db, limite=None):
    consulta = select(m.ContenidoBlog).where(m.ContenidoBlog.activo).order_by(m.ContenidoBlog.fecha_publicacion.desc())
    return db.scalars(consulta.limit(limite) if limite else consulta).all()


def _clave_mes(articulo):
    f = articulo.fecha_publicacion
    return (f.strftime('%Y-%m'), f'{MESES_ES[f.month]} {f.year}') if f else ('sin-fecha', 'Sin fecha')


def _agrupar_por_mes(articulos):
    """Agrupa artículos (ya ordenados DESC por fecha) en bloques por mes/año para la barra lateral de archivo."""
    grupos = {}
    for articulo in articulos:
        key, label = _clave_mes(articulo)
        grupos.setdefault(key, {'key': key, 'label': label, 'articulos': []})['articulos'].append(articulo)
    return list(grupos.values())


@router.get('/', name='public.index')
def index(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, 'public/index.html', {
        'seo': db.get(m.ConfiguracionSeo, 1),
        'modulos': db.scalars(select(m.Modulo).where(m.Modulo.activo).order_by(m.Modulo.orden)).all(),
        'hero': db.get(m.ContenidoHero, 1),
        'carousel': _todos(db, m.ContenidoCarousel, m.ContenidoCarousel.orden),
        'services': _todos(db, m.ContenidoService, m.ContenidoService.orden),
        'gallery': _todos(db, m.ContenidoGallery, m.ContenidoGallery.orden),
        'testimonials': _todos(db, m.ContenidoTestimonial, m.ContenidoTestimonial.orden),
        'blog': _articulos_publicados(db, limite=3),
        'about': db.get(m.ContenidoAbout, 1),
        'about_bloques': _todos(db, m.ContenidoAboutBloque, m.ContenidoAboutBloque.orden),
        'contact_submodulos': _todos(db, m.ContactSubmodulo, m.ContactSubmodulo.orden),
        'contact_datos': db.get(m.ContactDatos, 1),
        'contact_mapa': db.get(m.ContactMapa, 1),
    })


@router.get('/articulo/{id}', name='public.ver_articulo')
def ver_articulo(id: int, request: Request, db: Session = Depends(get_db)):
    articulo = db.get(m.ContenidoBlog, id)
    # Los borradores (activo = 0) solo los ve el admin logueado, para previsualizarlos.
    if not articulo or (not articulo.activo and not request.session.get('admin_id')):
        return PlainTextResponse('Artículo no encontrado', status_code=404)

    return templates.TemplateResponse(request, 'public/post.html', {
        'articulo': articulo,
        'grupos': _agrupar_por_mes(_articulos_publicados(db)),
        'mes_actual': _clave_mes(articulo)[0],
    })


@router.get('/blog', name='public.blog_archivo')
def blog_archivo(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(request, 'public/blog_index.html', {
        'grupos': _agrupar_por_mes(_articulos_publicados(db)),
        'seo': db.get(m.ConfiguracionSeoBlog, 1),
    })


@router.post('/contacto', name='public.enviar_contacto', dependencies=[Depends(verificar_csrf)])
def enviar_contacto(
    request: Request,
    db: Session = Depends(get_db),
    nombre: str = Form(''),
    email: str = Form(''),
    mensaje: str = Form(''),
    sitio_web: str = Form(''),
):
    volver = RedirectResponse(request.app.url_path_for('public.index') + '#contact', status_code=303)
    nombre, email, mensaje = nombre.strip(), email.strip(), mensaje.strip()

    if sitio_web:  # honeypot anti-spam: campo oculto que un humano nunca llena
        return volver
    if not nombre or not email or not mensaje:
        flash(request, 'Por favor completa todos los campos del formulario.', 'danger')
        return volver
    if not EMAIL_REGEX.match(email):
        flash(request, 'Por favor ingresa un correo electrónico válido.', 'danger')
        return volver

    db.add(m.MensajeContacto(nombre=nombre, email=email, mensaje=mensaje))
    db.commit()
    flash(request, '¡Gracias! Tu mensaje fue enviado correctamente, te contactaremos pronto.', 'success')
    return volver
