import re

from sqlalchemy import select

from app import models as m
from app.consentimiento import COOKIE, VERSION_POLITICA

BANNER_OCULTO = re.compile(r'id="banner-cookies"[^>]*\shidden')


def _token(client):
    return re.search(r'name="csrf-token" content="(\w+)"', client.get('/').text).group(1)


def _decidir(client, decision):
    return client.post('/api/consentimiento', json={'decision': decision}, headers={'X-CSRFToken': _token(client)})


def _decisiones(db):
    db.rollback()  # cierra la transacción: MariaDB (REPEATABLE READ) si no, repite la foto anterior
    return [c.decision for c in db.scalars(select(m.Consentimiento).order_by(m.Consentimiento.id))]


def test_banner_visible_hasta_decidir_y_luego_oculto(client, db):
    assert not BANNER_OCULTO.search(client.get('/').text)
    r = _decidir(client, 'aceptado')
    assert r.status_code == 204
    assert 'httponly' in r.headers['set-cookie'].lower()
    html = client.get('/').text
    assert BANNER_OCULTO.search(html) and 'data-consentimiento="aceptado"' in html
    assert _decisiones(db) == ['aceptado']


def test_retirar_consentimiento_borra_cookies_analiticas(client, db):
    _decidir(client, 'aceptado')
    r = _decidir(client, 'rechazado')
    assert '_visitor_id=""' in r.headers.get('set-cookie', '') or '_visitor_id=;' in r.headers.get('set-cookie', '')
    assert _decisiones(db) == ['aceptado', 'retirado']
    assert client.cookies.get(COOKIE).startswith(f'rechazado.{VERSION_POLITICA}.')


def test_exige_csrf_y_decision_valida(client, db):
    client.get('/')
    assert client.post('/api/consentimiento', json={'decision': 'aceptado'}).status_code == 400
    assert client.post('/api/consentimiento', json={'decision': 'quizas'}, headers={'X-CSRFToken': _token(client)}).status_code == 422
    assert _decisiones(db) == []


def test_cambio_de_version_vuelve_a_pedir_consentimiento(client):
    client.cookies.set(COOKIE, 'aceptado.2020-01.abc')
    assert not BANNER_OCULTO.search(client.get('/').text)


def test_politica_muestra_responsable_y_correo(client, db):
    legal = db.get(m.ConfiguracionLegal, 1)
    legal.razon_social, legal.rut = 'Clases Ana SpA', '76.123.456-7'
    db.commit()
    html = client.get('/privacidad').text
    assert 'Clases Ana SpA' in html and '76.123.456-7' in html
    assert 'contacto@tudominio.cl' in html  # sin correo propio, usa el de Contacto


def test_admin_edita_datos_legales(admin):
    r = admin.put('/api/admin/legal', json={'razon_social': 'Mi Empresa', 'rut': '1-9', 'email_privacidad': 'privacidad@x.cl'})
    assert r.json() == {'razon_social': 'Mi Empresa', 'rut': '1-9', 'email_privacidad': 'privacidad@x.cl'}
