import time

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from werkzeug.security import check_password_hash, generate_password_hash

from .. import models as m
from ..db import get_db
from ..schemas import CambioPassword, Login, Sesion
from ..web import csrf_token, verificar_csrf

router = APIRouter(prefix='/api/auth', tags=['auth'], dependencies=[Depends(verificar_csrf)])

# Freno a fuerza bruta: máx. MAX_INTENTOS fallos por IP en VENTANA_SEGUNDOS.
# shortcut: contador en memoria del proceso; se reinicia con el servidor y no se comparte entre
# varios procesos. Si Passenger levanta varios, pasar a una tabla en MySQL.
MAX_INTENTOS = 5
VENTANA_SEGUNDOS = 15 * 60
_fallos_por_ip: dict[str, list[float]] = {}


def _fallos_recientes(ip):
    limite = time.time() - VENTANA_SEGUNDOS
    fallos = [t for t in _fallos_por_ip.get(ip, []) if t > limite]
    if fallos:
        _fallos_por_ip[ip] = fallos
    else:
        _fallos_por_ip.pop(ip, None)  # no acumular IPs viejas en memoria
    return fallos


def admin_actual(request: Request, db: Session = Depends(get_db)) -> m.Admin:
    """Dependencia: exige sesión de admin. Responde 401 si no hay."""
    admin = db.get(m.Admin, request.session.get('admin_id') or 0)
    if not admin:
        raise HTTPException(401, 'Inicia sesión para continuar.')
    return admin


def _sesion(request, db, admin):
    no_leidos = db.scalar(select(func.count()).select_from(m.MensajeContacto).where(~m.MensajeContacto.leido)) if admin else 0
    return Sesion(usuario=admin.username if admin else None, csrf_token=csrf_token(request), mensajes_no_leidos=no_leidos)


@router.get('/sesion', response_model=Sesion, summary='Usuario actual y token CSRF (llamar al cargar el panel)')
def ver_sesion(request: Request, db: Session = Depends(get_db)):
    return _sesion(request, db, db.get(m.Admin, request.session.get('admin_id') or 0))


@router.post('/login', response_model=Sesion)
def login(datos: Login, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else 'desconocida'
    if len(_fallos_recientes(ip)) >= MAX_INTENTOS:
        raise HTTPException(429, 'Demasiados intentos fallidos. Espera 15 minutos e inténtalo de nuevo.')

    admin = db.scalar(select(m.Admin).where(m.Admin.username == datos.username))
    if not admin or not check_password_hash(admin.password_hash, datos.password):
        _fallos_por_ip.setdefault(ip, []).append(time.time())
        raise HTTPException(401, 'Usuario o contraseña incorrectos.')

    _fallos_por_ip.pop(ip, None)
    request.session.clear()  # sesión nueva al entrar: también renueva el token CSRF
    request.session['admin_id'] = admin.id
    return _sesion(request, db, admin)


@router.post('/logout', status_code=204)
def logout(request: Request):
    request.session.clear()
    return Response(status_code=204)


@router.post('/cambiar-password', status_code=204)
def cambiar_password(datos: CambioPassword, admin: m.Admin = Depends(admin_actual), db: Session = Depends(get_db)):
    if not check_password_hash(admin.password_hash, datos.actual):
        raise HTTPException(400, 'La contraseña actual no es correcta.')
    if datos.nueva != datos.confirmar:
        raise HTTPException(400, 'La nueva contraseña y su confirmación no coinciden.')
    admin.password_hash = generate_password_hash(datos.nueva)
    db.commit()
    return Response(status_code=204)
