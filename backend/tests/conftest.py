"""
Los tests corren contra una base MySQL/MariaDB aparte (nunca la de desarrollo), que se vacía
y recrea en cada test. Por defecto usa la de desarrollo con sufijo _test; se puede cambiar con TEST_DATABASE_URL.
"""
import os
import re
import tempfile
from pathlib import Path

import pytest
from dotenv import dotenv_values

_dev_url = dotenv_values(Path(__file__).resolve().parent.parent / '.env').get('DATABASE_URL', '')
os.environ['DATABASE_URL'] = os.environ.get('TEST_DATABASE_URL') or re.sub(r'/(\w+)\?', r'/\1_test?', _dev_url)
os.environ.setdefault('SECRET_KEY', 'clave-solo-para-tests')
os.environ.setdefault('ADMIN_PASSWORD', 'clave-admin-tests')
os.environ['UPLOADS_DIR'] = tempfile.mkdtemp(prefix='dl-uploads-')

from fastapi.testclient import TestClient  # noqa: E402

from app.db import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.seed import sembrar  # noqa: E402

assert engine.url.database.endswith('_test'), 'Los tests solo deben correr contra una base *_test'


@pytest.fixture
def db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as sesion:
        sembrar(sesion)
        yield sesion


@pytest.fixture
def client(db):
    from app.api import auth
    auth._fallos_por_ip.clear()  # el freno de fuerza bruta es global al proceso
    return TestClient(app)


@pytest.fixture
def admin(client):
    """Cliente con sesión de admin iniciada y el header CSRF ya puesto."""
    token = client.get('/api/auth/sesion').json()['csrf_token']
    r = client.post('/api/auth/login', json={'username': 'admin', 'password': 'clave-admin-tests'},
                    headers={'X-CSRFToken': token})
    assert r.status_code == 200, r.text
    client.headers['X-CSRFToken'] = r.json()['csrf_token']
    return client
