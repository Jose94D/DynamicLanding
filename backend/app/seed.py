"""
Datos por defecto (mismos que el database.py original). Idempotente: solo inserta lo que falta,
nunca pisa contenido ya editado.

Uso (desde backend/, después de `alembic upgrade head`):
    python -m app.seed
"""
import os
import secrets

from werkzeug.security import generate_password_hash

from . import models as m
from .db import SessionLocal

MODULOS = [
    ('hero', 'Banner Principal (Hero)', 1),
    ('about', 'Sobre Nosotros', 2),
    ('carousel', 'Carrusel de Imágenes', 3),
    ('services', 'Servicios', 4),
    ('gallery', 'Galería de Productos', 5),
    ('testimonials', 'Testimonios de Clientes', 6),
    ('social', 'Módulo de Redes Sociales (Feed)', 7),
    ('blog_preview', 'Últimas Entradas del Blog', 8),
    ('contact', 'Formulario de Contacto', 9),
]
CONTACT_SUBMODULOS = [
    ('mensajes', 'Formulario de Mensajes', 1),
    ('mapa', 'Mapa de Ubicación', 2),
    ('datos', 'Datos de Contacto', 3),
]
ABOUT_BLOQUES = [
    ('historia', 'Descripción / Historia', 1),
    ('mision', 'Visión o Misión (Texto destacado)', 2),
    ('imagen', 'Imagen', 3),
]


def _agregar_si_falta(db, modelo, **campos):
    if db.get(modelo, campos['id']) is None:
        db.add(modelo(**campos))


def sembrar(db):
    for modelo, filas in ((m.Modulo, MODULOS), (m.ContactSubmodulo, CONTACT_SUBMODULOS), (m.ContenidoAboutBloque, ABOUT_BLOQUES)):
        for id_, nombre, orden in filas:
            _agregar_si_falta(db, modelo, id=id_, nombre_legible=nombre, activo=True, orden=orden)

    _agregar_si_falta(db, m.ContenidoHero, id=1, titulo='Bienvenido a tu Landing Page',
                      subtitulo='Edita este texto desde el panel de administración',
                      texto_boton='Contáctanos', url_boton='#contact')
    _agregar_si_falta(db, m.ContenidoAbout, id=1, titulo='Sobre Nosotros',
                      descripcion='Cuenta aquí la historia de tu negocio.',
                      mision='Tu misión o propuesta de valor.')
    _agregar_si_falta(db, m.ContactDatos, id=1, titulo='Hablemos',
                      subtitulo='¿Tienes alguna duda o quieres agendar una clase? Estoy disponible para ayudarte.',
                      telefono='+56 9 1234 5678', email='contacto@tudominio.cl',
                      ubicacion_texto='Santiago, Chile', horario='Lun - Vie | 9:00 - 18:00')
    _agregar_si_falta(db, m.ContactMapa, id=1, direccion='Santiago, Chile')
    _agregar_si_falta(db, m.ConfiguracionSeo, id=1, meta_titulo='Mi Landing Page',
                      meta_descripcion='Descripción por defecto para motores de búsqueda')
    _agregar_si_falta(db, m.ConfiguracionSeoBlog, id=1, meta_titulo='Blog', meta_descripcion='Artículos y novedades')

    # Admin: usa ADMIN_USERNAME/ADMIN_PASSWORD del entorno. Si no hay contraseña, genera una y la
    # muestra UNA sola vez en consola: no queda guardada en ningún archivo.
    if db.query(m.Admin).count() == 0:
        username = os.environ.get('ADMIN_USERNAME', 'admin')
        password = os.environ.get('ADMIN_PASSWORD')
        generada = password is None
        if generada:
            password = secrets.token_urlsafe(12)
        db.add(m.Admin(username=username, password_hash=generate_password_hash(password)))
        if generada:
            print(
                '\n🔑 Se creó el usuario admin con una contraseña generada automáticamente:\n'
                f'    Usuario:    {username}\n'
                f'    Contraseña: {password}\n'
                '    Guárdala ahora — no se volverá a mostrar.\n'
            )

    db.commit()


if __name__ == '__main__':
    with SessionLocal() as sesion:
        sembrar(sesion)
    print('Datos por defecto listos.')
