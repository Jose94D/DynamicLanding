import re

import pytest
from sqlalchemy import func, select

from app import analiticas
from app import models as m


@pytest.fixture(autouse=True)
def sin_limite_previo():
    analiticas._eventos_por_ip.clear()


def _aceptar(client):
    token = re.search(r'name="csrf-token" content="(\w+)"', client.get('/').text).group(1)
    assert client.post('/api/consentimiento', json={'decision': 'aceptado'}, headers={'X-CSRFToken': token}).status_code == 204


def _pageview(client, ruta='/', **headers):
    # Como sendBeacon: JSON en texto plano
    return client.post('/api/eventos', content=f'{{"tipo": "pageview", "ruta": "{ruta}"}}',
                       headers={'Content-Type': 'text/plain;charset=UTF-8', **headers})


def _contar(db, modelo):
    db.rollback()  # cierra la transacción: MariaDB (REPEATABLE READ) si no, repite la foto anterior
    return db.scalar(select(func.count()).select_from(modelo))


def test_sin_consentimiento_no_guarda_nada(client, db):
    r = _pageview(client)
    assert r.status_code == 204 and 'set-cookie' not in r.headers
    assert _contar(db, m.AnaliticaEvento) == 0


def test_con_consentimiento_guarda_y_reusa_la_sesion(client, db):
    _aceptar(client)
    r = _pageview(client, '/')
    cookies = r.headers.get_list('set-cookie')
    assert any(c.startswith('_session_id=') and 'HttpOnly' in c and 'Max-Age=1800' in c for c in cookies)
    assert any(c.startswith('_visitor_id=') and 'Max-Age=7776000' in c for c in cookies)

    _pageview(client, '/blog')
    assert _contar(db, m.AnaliticaSesion) == 1
    assert [e.ruta for e in db.scalars(select(m.AnaliticaEvento).order_by(m.AnaliticaEvento.id))] == ['/', '/blog']


def test_sesion_nueva_mismo_visitante_al_vencer_la_sesion(client, db):
    _aceptar(client)
    _pageview(client)
    client.cookies.delete('_session_id')  # el navegador la borra a los 30 min
    _pageview(client)
    db.rollback()  # cierra la transacción: MariaDB (REPEATABLE READ) si no, repite la foto anterior
    sesiones = db.scalars(select(m.AnaliticaSesion)).all()
    assert len(sesiones) == 2 and sesiones[0].visitor_id == sesiones[1].visitor_id


def test_guarda_dispositivo_y_origen_de_la_visita(client, db):
    _aceptar(client)
    iphone = 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 Version/18.1 Mobile/15E148 Safari/604.1'
    client.post('/api/eventos', content='{"tipo": "pageview", "ruta": "/", "referente": "https://l.instagram.com/x?u=1",'
                                        ' "utm_source": null}', headers={'User-Agent': iphone})
    db.rollback()  # cierra la transacción: MariaDB (REPEATABLE READ) si no, repite la foto anterior
    s = db.scalars(select(m.AnaliticaSesion)).one()
    assert (s.dispositivo, s.navegador, s.sistema, s.origen, s.referente) == ('movil', 'Safari', 'iOS', 'social', 'l.instagram.com')


def test_metricas_unicos_nuevos_recurrentes_y_desgloses(admin, db):
    from datetime import datetime, timedelta
    hace = lambda d: datetime.now() - timedelta(days=d)  # noqa: E731
    sesion = lambda sid, vid, dias, disp='movil', origen='buscador': m.AnaliticaSesion(  # noqa: E731
        session_id=sid * 32, visitor_id=vid * 32, inicio=hace(dias), dispositivo=disp, navegador='Chrome', origen=origen)
    db.add_all([
        sesion('a', '1', 60), sesion('b', '1', 2),                      # visitante 1: vino antes del período -> recurrente
        sesion('c', '2', 5, 'escritorio', 'social'), sesion('d', '2', 1),  # visitante 2: primera vez en el período -> nuevo
        sesion('e', '3', 40),                                           # visitante 3: fuera del período, no cuenta
    ])
    db.commit()

    c = admin.get('/api/admin/analiticas?dias=30').json()['consentidas']
    assert (c['visitas'], c['visitantes_unicos'], c['nuevos'], c['recurrentes']) == (3, 2, 1, 1)
    assert c['por_dispositivo'] == [{'nombre': 'movil', 'total': 2}, {'nombre': 'escritorio', 'total': 1}]
    assert c['por_origen'][0] == {'nombre': 'buscador', 'total': 2}


def _enviar_formulario(client):
    token = re.search(r'name="csrf_token" value="(\w+)"', client.get('/').text).group(1)
    r = client.post('/contacto', data={'csrf_token': token, 'nombre': 'Ana', 'email': 'ana@x.cl', 'mensaje': 'Hola'})
    assert 'Tu mensaje fue enviado correctamente' in r.text


def test_envio_del_formulario_cuenta_como_conversion(admin, db):
    _aceptar(admin)
    _pageview(admin, '/')
    _enviar_formulario(admin)
    _enviar_formulario(admin)  # dos envíos en la misma visita = una visita convertida

    db.rollback()
    assert [e.tipo for e in db.scalars(select(m.AnaliticaEvento).order_by(m.AnaliticaEvento.id))] == \
        ['pageview', 'form_submit', 'form_submit']
    a = admin.get('/api/admin/analiticas?dias=7').json()
    assert a['mensajes_recibidos'] == 2
    assert (a['consentidas']['visitas_con_envio'], a['consentidas']['tasa_conversion']) == (1, 100.0)


def test_envio_sin_consentimiento_guarda_el_mensaje_pero_no_la_conversion(client, db):
    _enviar_formulario(client)
    assert _contar(db, m.MensajeContacto) == 1
    assert _contar(db, m.AnaliticaEvento) == 0


def test_el_navegador_no_puede_inventar_conversiones(client):
    _aceptar(client)
    assert client.post('/api/eventos', content='{"tipo": "form_submit", "ruta": "/contacto"}').status_code == 422


def _evento(client, tipo, segundos=0):
    return client.post('/api/eventos', content=f'{{"tipo": "{tipo}", "ruta": "/", "segundos": {segundos}}}')


def test_latidos_suman_duracion_sin_guardar_eventos(client, db):
    _aceptar(client)
    _pageview(client)
    for s in (15, 15, 7, 500):  # 500 s en un latido no es creíble: se limita a 30
        assert _evento(client, 'heartbeat', s).status_code == 204
    db.rollback()
    assert db.scalars(select(m.AnaliticaSesion)).one().segundos_activos == 15 + 15 + 7 + 30
    assert _contar(db, m.AnaliticaEvento) == 1  # solo el pageview


def test_galeria_y_duracion_en_las_metricas(admin, db):
    _aceptar(admin)
    _pageview(admin)
    _evento(admin, 'gallery_open')
    _evento(admin, 'gallery_navigate')
    _evento(admin, 'gallery_navigate')
    _evento(admin, 'heartbeat', 20)
    c = admin.get('/api/admin/analiticas?dias=7').json()['consentidas']
    assert (c['aperturas_galeria'], c['navegaciones_galeria'], c['visitas_con_galeria'], c['duracion_media']) == (1, 2, 1, 20)


def test_sin_visita_abierta_solo_un_pageview_la_crea(client, db):
    _aceptar(client)
    assert _evento(client, 'gallery_open').status_code == 204
    assert _evento(client, 'heartbeat', 15).status_code == 204
    assert _contar(db, m.AnaliticaSesion) == 0


def test_bots_no_cuentan(client, db):
    client.get('/', headers={'User-Agent': 'Googlebot/2.1'})
    assert _contar(db, m.AnaliticaVisita) == 0
    client.get('/')
    assert _contar(db, m.AnaliticaVisita) == 1


def test_rechaza_otro_origen_y_eventos_invalidos(client, db):
    _aceptar(client)
    assert _pageview(client, Origin='https://otro-sitio.com').status_code == 403
    assert _pageview(client, 'sin-barra').status_code == 422
    assert client.post('/api/eventos', content='{"tipo": "inventado", "ruta": "/"}').status_code == 422
    assert client.post('/api/eventos', content='x' * 3000).status_code == 413
    assert _contar(db, m.AnaliticaEvento) == 0


def test_limite_de_eventos_por_ip(client, monkeypatch):
    monkeypatch.setattr(analiticas, 'MAX_EVENTOS_POR_MINUTO', 2)
    assert [_pageview(client).status_code for _ in range(3)] == [204, 204, 429]
