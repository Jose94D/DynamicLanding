import io
import os
from pathlib import Path

from PIL import Image


def _png(ancho=2400, alto=100):
    buf = io.BytesIO()
    Image.new('RGB', (ancho, alto), 'red').save(buf, format='PNG')
    return ('foto.png', buf.getvalue(), 'image/png')


# ---------- Auth ----------
def test_sin_sesion_responde_401(client):
    assert client.get('/api/admin/hero').status_code == 401


def test_login_exige_csrf(client):
    r = client.post('/api/auth/login', json={'username': 'admin', 'password': 'clave-admin-tests'})
    assert r.status_code == 400


def test_login_incorrecto_y_freno_de_fuerza_bruta(client):
    token = client.get('/api/auth/sesion').json()['csrf_token']
    malo = {'username': 'admin', 'password': 'nop'}
    codigos = [client.post('/api/auth/login', json=malo, headers={'X-CSRFToken': token}).status_code for _ in range(6)]
    assert codigos == [401] * 5 + [429]


def test_modificar_sin_csrf_es_rechazado(admin):
    r = admin.put('/api/admin/hero', json={'titulo': 'X'}, headers={'X-CSRFToken': 'falso'})
    assert r.status_code == 400


def test_sesion_y_logout(admin):
    assert admin.get('/api/auth/sesion').json()['usuario'] == 'admin'
    assert admin.post('/api/auth/logout').status_code == 204
    assert admin.get('/api/admin/hero').status_code == 401


def test_cambiar_password(admin):
    datos = {'actual': 'clave-admin-tests', 'nueva': 'otra-clave-123', 'confirmar': 'distinta-123'}
    assert admin.post('/api/auth/cambiar-password', json=datos).status_code == 400
    datos['confirmar'] = 'otra-clave-123'
    assert admin.post('/api/auth/cambiar-password', json=datos).status_code == 204


def test_borrador_visible_para_admin(admin):
    id_ = admin.post('/api/admin/blog', json={'titulo': 'Borrador', 'extracto': 'e', 'contenido': 'c', 'activo': False}).json()['id']
    assert admin.get(f'/articulo/{id_}').status_code == 200


def test_comando_cambiar_clave(client, monkeypatch):
    from app import cambiar_clave
    monkeypatch.setattr(cambiar_clave, 'getpass', lambda _: 'clave-nueva-123')
    cambiar_clave.main(['admin'])
    token = client.get('/api/auth/sesion').json()['csrf_token']
    r = client.post('/api/auth/login', json={'username': 'admin', 'password': 'clave-nueva-123'}, headers={'X-CSRFToken': token})
    assert r.status_code == 200


# ---------- Contenido ----------
def test_hero_y_modulos(admin):
    assert admin.put('/api/admin/hero', json={'titulo': '  Nuevo título  '}).json()['titulo'] == 'Nuevo título'
    estados = [{'id': 'hero', 'activo': False, 'orden': 9}]
    modulos = admin.put('/api/admin/modulos', json=estados).json()
    assert modulos[-1] == {'id': 'hero', 'nombre_legible': 'Banner Principal (Hero)', 'activo': False, 'orden': 9}
    assert 'Nuevo título' not in admin.get('/').text  # el módulo oculto no se muestra en la landing


def test_seo_valida_largo(admin):
    r = admin.put('/api/admin/seo', json={'meta_titulo': 'x' * 61, 'meta_descripcion': 'ok'})
    assert r.status_code == 422


def test_contacto_y_orden_de_submodulos(admin):
    actual = admin.get('/api/admin/contacto').json()
    actual['direccion'] = 'Valparaíso, Chile'
    actual['submodulos'] = [{'id': 'mapa', 'activo': False}]
    assert admin.put('/api/admin/contacto', json=actual).json()['direccion'] == 'Valparaíso, Chile'
    assert admin.put('/api/admin/contacto/submodulos/orden', json={'orden': ['datos', 'mapa', 'mensajes']}).status_code == 204
    subs = admin.get('/api/admin/contacto').json()['submodulos']
    assert [(s['id'], s['activo']) for s in subs] == [('datos', True), ('mapa', False), ('mensajes', True)]


def test_redes_no_expone_el_token(admin):
    r = admin.put('/api/admin/redes/instagram', json={'access_token': 'secreto', 'account_id': '123', 'activo_api': True})
    assert r.json() == {'plataforma': 'instagram', 'account_id': '123', 'activo_api': True, 'tiene_token': True}
    # Sin access_token se conserva el guardado
    r = admin.put('/api/admin/redes/instagram', json={'account_id': '123', 'activo_api': False})
    assert r.json()['tiene_token'] is True
    assert 'secreto' not in admin.get('/api/admin/redes').text
    assert admin.put('/api/admin/redes/tiktok', json={'activo_api': True}).status_code == 404


# ---------- Listas con imágenes ----------
def test_galeria_sube_optimiza_reordena_y_borra(admin):
    a = admin.post('/api/admin/galeria', files={'imagen': _png()}, data={'titulo': 'A'}).json()
    b = admin.post('/api/admin/galeria', files={'imagen': _png()}, data={'titulo': 'B'}).json()
    ruta_a = Path(os.environ['UPLOADS_DIR']) / 'gallery' / a['nombre_archivo']
    assert Image.open(ruta_a).width == 1200  # redimensionada al máximo de la galería

    assert admin.put('/api/admin/galeria/orden', json={'orden': [b['id'], a['id']]}).status_code == 204
    assert [x['titulo'] for x in admin.get('/api/admin/galeria').json()] == ['B', 'A']

    assert admin.delete(f"/api/admin/galeria/{a['id']}").status_code == 204
    assert not ruta_a.exists()


def test_subida_rechaza_archivo_que_no_es_imagen(admin):
    r = admin.post('/api/admin/carrusel', files={'imagen': ('x.jpg', b'no soy una imagen', 'image/jpeg')})
    assert r.status_code == 400


def test_servicios_crud(admin):
    s = admin.post('/api/admin/servicios', json={'titulo': 'Clases', 'descripcion': 'Online'}).json()
    assert s['orden'] == 1 and s['icono'] == 'bi-star'
    assert admin.put(f"/api/admin/servicios/{s['id']}", json={'titulo': 'Clases 2', 'descripcion': 'x'}).json()['titulo'] == 'Clases 2'
    assert admin.delete(f"/api/admin/servicios/{s['id']}").status_code == 204
    assert admin.delete(f"/api/admin/servicios/{s['id']}").status_code == 404


def test_testimonio_valida_calificacion(admin):
    assert admin.post('/api/admin/testimonios', data={'nombre': 'Ana', 'texto': 'Bien', 'calificacion': 6}).status_code == 422
    assert admin.post('/api/admin/testimonios', data={'nombre': 'Ana', 'texto': 'Bien'}).json()['calificacion'] == 5


# ---------- Blog, mensajes, analíticas ----------
def test_blog_slug_unico_y_no_cambia_al_editar(admin):
    a = admin.post('/api/admin/blog', json={'titulo': '¡Hola Mundo!', 'extracto': 'e', 'contenido': 'c'}).json()
    b = admin.post('/api/admin/blog', json={'titulo': 'Hola mundo', 'extracto': 'e', 'contenido': 'c'}).json()
    assert a['slug'] == 'hola-mundo' and b['slug'].startswith('hola-mundo-')
    editado = admin.put(f"/api/admin/blog/{a['id']}", json={'titulo': 'Otro', 'extracto': 'e', 'contenido': 'c'}).json()
    assert editado['slug'] == 'hola-mundo'


def test_mensajes_y_contador_de_no_leidos(admin, db):
    from app import models as m
    db.add(m.MensajeContacto(nombre='Ana', email='a@x.cl', mensaje='Hola'))
    db.commit()
    assert admin.get('/api/auth/sesion').json()['mensajes_no_leidos'] == 1
    id_ = admin.get('/api/admin/mensajes').json()['mensajes'][0]['id']
    assert admin.post(f'/api/admin/mensajes/{id_}/leido').json()['leido'] is True
    assert admin.get('/api/admin/mensajes').json()['no_leidos'] == 0


def test_analiticas_cuenta_paginas_vistas_anonimas(admin):
    admin.get('/')
    admin.get('/blog')
    datos = admin.get('/api/admin/analiticas?dias=7').json()
    assert datos['paginas_vistas'] == 2
    assert len(datos['serie']) == 7 and datos['serie'][-1]['total'] == 2  # 7 días sin huecos; hoy al final
    assert admin.get('/api/admin/analiticas?dias=365').json()['serie'][-1]['total'] == 2  # por mes
    assert admin.get('/api/admin/analiticas?dias=15').status_code == 422
