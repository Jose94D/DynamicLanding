import re
from datetime import datetime, timedelta

from sqlalchemy import func, select

from app import models as m
from app.consentimiento import COOKIE
from app.retencion import aplicar


def _token(client):
    return re.search(r'name="csrf-token" content="(\w+)"', client.get('/privacidad').text).group(1)


def _contar(db, modelo):
    db.rollback()
    return db.scalar(select(func.count()).select_from(modelo))


def _visita(db, sid, vid, dias_atras, **extra):
    db.add(m.AnaliticaSesion(session_id=sid * 32, visitor_id=vid * 32, inicio=datetime.now() - timedelta(days=dias_atras), **extra))
    db.flush()


# ---------- Comparativa con el período anterior ----------
def test_compara_con_el_periodo_anterior(admin, db):
    _visita(db, 'a', '1', 3, segundos_activos=60)    # período actual (últimos 7 días)
    _visita(db, 'b', '2', 10, segundos_activos=30)   # período anterior (días 8 a 14)
    _visita(db, 'c', '3', 12, segundos_activos=30)
    _visita(db, 'd', '4', 30)                        # fuera de ambos
    db.add(m.AnaliticaVisita(ruta='/', fecha=datetime.now() - timedelta(days=9)))
    db.commit()

    a = admin.get('/api/admin/analiticas?dias=7').json()
    assert (a['consentidas']['visitas'], a['anterior']['consentidas']['visitas']) == (1, 2)
    assert (a['consentidas']['duracion_media'], a['anterior']['consentidas']['duracion_media']) == (60, 30)
    assert (a['paginas_vistas'], a['anterior']['paginas_vistas']) == (0, 1)


# ---------- Eliminar mis datos ----------
def test_eliminar_mis_datos_borra_solo_lo_de_este_navegador(client, db):
    _visita(db, 'a', '1', 1)
    db.add(m.AnaliticaEvento(session_id='a' * 32, tipo='pageview', ruta='/'))
    _visita(db, 'b', '2', 1)  # otro visitante: no se toca
    db.commit()
    client.cookies.set('_visitor_id', '1' * 32)
    client.cookies.set(COOKIE, 'aceptado.2026-11.x')

    r = client.post('/api/privacidad/eliminar-mis-datos', headers={'X-CSRFToken': _token(client)})
    assert r.status_code == 200 and r.json() == {'visitas_eliminadas': 1}
    assert any(c.startswith(f'{COOKIE}=rechazado.') for c in r.headers.get_list('set-cookie'))  # consentimiento retirado
    assert _contar(db, m.AnaliticaSesion) == 1 and _contar(db, m.AnaliticaEvento) == 0  # eventos borrados en cascada
    assert db.scalars(select(m.Consentimiento.decision)).all() == ['eliminado']


def test_eliminar_mis_datos_exige_csrf(client):
    client.get('/privacidad')
    assert client.post('/api/privacidad/eliminar-mis-datos').status_code == 400


# ---------- Retención ----------
def test_retencion_borra_lo_vencido_y_conserva_lo_reciente(db):
    _visita(db, 'a', '1', 400)   # más de 13 meses
    _visita(db, 'b', '2', 300)
    db.add_all([
        m.MensajeContacto(nombre='Viejo', email='v@x.cl', mensaje='x', fecha_envio=datetime.now() - timedelta(days=800)),
        m.MensajeContacto(nombre='Nuevo', email='n@x.cl', mensaje='x'),
        m.AnaliticaVisita(ruta='/', fecha=datetime.now() - timedelta(days=900)),  # conteo anónimo: se conserva
    ])
    db.commit()

    assert aplicar(db) == {'visitas': 1, 'mensajes': 1}
    assert _contar(db, m.AnaliticaSesion) == 1 and _contar(db, m.MensajeContacto) == 1
    assert _contar(db, m.AnaliticaVisita) == 1


# ---------- Registro de consentimientos en el panel ----------
def test_panel_muestra_registro_de_consentimientos(admin):
    token = re.search(r'name="csrf-token" content="(\w+)"', admin.get('/').text).group(1)
    admin.post('/api/consentimiento', json={'decision': 'aceptado'}, headers={'X-CSRFToken': token})
    r = admin.get('/api/admin/legal/consentimientos').json()
    assert r['ultimos_30_dias'] == {'aceptado': 1} and r['recientes'][0]['decision'] == 'aceptado'
