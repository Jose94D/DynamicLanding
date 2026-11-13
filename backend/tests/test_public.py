import re
from datetime import datetime

from sqlalchemy import func, select

from app import models as m


def _token(client):
    return re.search(r'name="csrf_token" value="(\w+)"', client.get('/').text).group(1)


def _contar(db, modelo):
    db.rollback()  # cierra la transacción: MariaDB (REPEATABLE READ) si no, repite la foto anterior
    return db.scalar(select(func.count()).select_from(modelo))


def test_landing_muestra_contenido_y_registra_visita(client, db):
    r = client.get('/')
    assert r.status_code == 200
    assert 'Bienvenido a tu Landing Page' in r.text
    assert _contar(db, m.AnaliticaVisita) == 1


def test_borrador_no_es_publico(client, db):
    db.add(m.ContenidoBlog(id=1, titulo='Borrador', slug='borrador', extracto='x', contenido='x', activo=False))
    db.commit()
    assert client.get('/articulo/1').status_code == 404


def test_blog_agrupa_por_mes(client, db):
    db.add(m.ContenidoBlog(titulo='Post de marzo', slug='marzo', extracto='x', contenido='<p>x</p>',
                           fecha_publicacion=datetime(2026, 3, 5)))
    db.commit()
    r = client.get('/blog')
    assert 'Marzo 2026' in r.text and 'Post de marzo' in r.text


def test_contacto_guarda_mensaje_y_muestra_aviso(client, db):
    r = client.post('/contacto', data={'csrf_token': _token(client), 'nombre': 'Ana', 'email': 'ana@x.cl', 'mensaje': 'Hola'})
    assert r.status_code == 200  # el cliente sigue la redirección a la landing
    assert 'Tu mensaje fue enviado correctamente' in r.text
    assert _contar(db, m.MensajeContacto) == 1


def test_contacto_rechaza_email_invalido_y_honeypot(client, db):
    token = _token(client)
    r = client.post('/contacto', data={'csrf_token': token, 'nombre': 'Ana', 'email': 'no-es-email', 'mensaje': 'Hola'})
    assert 'correo electrónico válido' in r.text
    client.post('/contacto', data={'csrf_token': token, 'nombre': 'Bot', 'email': 'b@x.cl', 'mensaje': 'spam', 'sitio_web': 'x'})
    assert _contar(db, m.MensajeContacto) == 0


def test_sin_base_de_datos_responde_503_con_mensaje(client):
    from sqlalchemy.exc import OperationalError

    from app.db import get_db
    from app.main import app

    def caida():
        raise OperationalError('SELECT 1', {}, Exception("Can't connect"))
        yield  # noqa: unreachable — la dependencia debe ser un generador, como get_db

    app.dependency_overrides[get_db] = caida
    try:
        r = client.get('/')
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 503 and 'iniciar_mariadb' in r.text


def test_contacto_sin_csrf_es_rechazado(client, db):
    r = client.post('/contacto', data={'nombre': 'Ana', 'email': 'ana@x.cl', 'mensaje': 'Hola'})
    assert r.status_code == 400
    assert _contar(db, m.MensajeContacto) == 0
