"""
Analíticas con consentimiento (Ley 21.719): recibe los eventos que envía landing.js.

- Solo registra algo si la cookie `_consent_status` dice 'aceptado'. Si no, responde 204 y no guarda nada
  (el conteo anónimo de `analiticas_visitas` sigue funcionando para todos, sin cookies).
- `_session_id` (30 min, se renueva con cada evento) y `_visitor_id` (90 días) son ids aleatorios que pone
  el servidor como httpOnly: el JavaScript de la página no los puede leer.
- No lleva CSRF porque sendBeacon no envía headers. En su lugar: solo acepta peticiones del mismo sitio
  (header Origin), tipos de evento conocidos, cuerpos pequeños y un límite de eventos por IP.
"""
import re
import time
import uuid
from typing import Literal
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import func
from sqlalchemy.orm import Session

from . import models as m
from .clasificar import clasificar_navegador, clasificar_origen, dominio, es_bot
from .config import COOKIE_SECURE
from .consentimiento import decision_vigente
from .db import get_db

DURACION_SESION = 30 * 60
DURACION_VISITANTE = 90 * 24 * 3600
MAX_BYTES = 2048
MAX_EVENTOS_POR_MINUTO = 120
ID_VALIDO = re.compile(r'[0-9a-f]{32}')

# shortcut: contador en memoria del proceso (cada proceso cuenta aparte); basta contra spam simple.
_eventos_por_ip: dict[str, list[float]] = {}


MAX_SEGUNDOS_LATIDO = 30  # el navegador late cada 15 s; más que esto en un solo latido no es creíble


class Evento(BaseModel):
    # 'form_submit' no está: lo registra el servidor al guardar el mensaje (registrar_en_sesion_actual).
    tipo: Literal['pageview', 'gallery_open', 'gallery_navigate', 'heartbeat']
    ruta: str = Field(pattern=r'^/', max_length=500)
    segundos: int = Field(0, ge=0, le=3600)  # solo 'heartbeat': tiempo visible desde el latido anterior
    # Solo se usan al crear la sesión (de dónde llegó la visita).
    referente: str | None = Field(None, max_length=500)
    utm_source: str | None = Field(None, max_length=100)
    utm_medium: str | None = Field(None, max_length=100)
    utm_campaign: str | None = Field(None, max_length=100)


async def _leer_evento(request: Request) -> Evento:
    """sendBeacon envía el JSON como text/plain, así que se lee el cuerpo a mano."""
    cuerpo = await request.body()
    if len(cuerpo) > MAX_BYTES:
        raise HTTPException(413, 'Evento demasiado grande.')
    try:
        return Evento.model_validate_json(cuerpo)
    except ValidationError as e:
        raise RequestValidationError(e.errors())


def _mismo_sitio(request: Request) -> bool:
    origen = request.headers.get('origin')
    return origen is None or urlparse(origen).netloc == request.headers.get('host')


def _limitar(ip: str):
    ahora = time.time()
    recientes = [t for t in _eventos_por_ip.get(ip, []) if t > ahora - 60]
    if len(recientes) >= MAX_EVENTOS_POR_MINUTO:
        raise HTTPException(429, 'Demasiados eventos.')
    if len(_eventos_por_ip) > 10_000:  # no crecer sin límite con IPs que ya no vuelven
        _eventos_por_ip.clear()
    _eventos_por_ip[ip] = recientes + [ahora]


def _id_de_cookie(request: Request, nombre: str) -> str | None:
    valor = request.cookies.get(nombre, '')
    return valor if ID_VALIDO.fullmatch(valor) else None


def registrar_en_sesion_actual(request: Request, db: Session, tipo: str, ruta: str):
    """Para eventos que decide el servidor (ej. 'form_submit' cuando el mensaje se guardó de verdad): se suman a
    la visita en curso. No se aceptan desde el navegador, así nadie puede inflar las conversiones con un script.
    Sin consentimiento o sin visita activa, no registra nada. No hace commit: va en la transacción de quien llama."""
    if decision_vigente(request) != 'aceptado':
        return
    sid = _id_de_cookie(request, '_session_id')
    sesion = db.get(m.AnaliticaSesion, sid) if sid else None
    if sesion is None or sesion.visitor_id != _id_de_cookie(request, '_visitor_id'):
        return
    sesion.ultima_actividad = func.now()
    db.add(m.AnaliticaEvento(session_id=sesion.session_id, tipo=tipo, ruta=ruta))


router = APIRouter(tags=['analíticas'])


@router.post('/api/eventos', status_code=204, summary='Registra un evento de analíticas (solo con consentimiento)')
def registrar_evento(request: Request, evento: Evento = Depends(_leer_evento), db: Session = Depends(get_db)):
    if not _mismo_sitio(request):
        raise HTTPException(403, 'Origen no permitido.')
    _limitar(request.client.host if request.client else 'desconocida')
    user_agent = request.headers.get('user-agent')
    if decision_vigente(request) != 'aceptado' or es_bot(user_agent):
        return Response(status_code=204)

    visitante = _id_de_cookie(request, '_visitor_id')
    visitante_nuevo = visitante is None
    if visitante_nuevo:
        visitante = uuid.uuid4().hex

    sid = _id_de_cookie(request, '_session_id')
    sesion = db.get(m.AnaliticaSesion, sid) if sid else None
    sin_visita = sesion is None or sesion.visitor_id != visitante
    if sin_visita and evento.tipo != 'pageview':  # solo una vista de página abre una visita
        return Response(status_code=204)

    if sin_visita:
        dispositivo, navegador, sistema = clasificar_navegador(user_agent)
        hay_utm = any((evento.utm_source, evento.utm_medium, evento.utm_campaign))
        sesion = m.AnaliticaSesion(
            session_id=uuid.uuid4().hex, visitor_id=visitante,
            dispositivo=dispositivo, navegador=navegador, sistema=sistema,
            origen=clasificar_origen(evento.referente, request.headers.get('host', ''), hay_utm),
            referente=dominio(evento.referente),
            utm_source=evento.utm_source, utm_medium=evento.utm_medium, utm_campaign=evento.utm_campaign,
        )
        db.add(sesion)
        db.flush()  # la sesión debe existir antes que el evento (clave foránea)
    else:
        sesion.ultima_actividad = func.now()

    if evento.tipo == 'heartbeat':
        # Duración real: se suman los intervalos con la página visible. No se guarda como evento (serían miles de filas).
        sesion.segundos_activos = m.AnaliticaSesion.segundos_activos + min(evento.segundos, MAX_SEGUNDOS_LATIDO)
    else:
        db.add(m.AnaliticaEvento(session_id=sesion.session_id, tipo=evento.tipo, ruta=evento.ruta))
    db.commit()

    respuesta = Response(status_code=204)
    opciones = dict(httponly=True, samesite='lax', secure=COOKIE_SECURE)
    respuesta.set_cookie('_session_id', sesion.session_id, max_age=DURACION_SESION, **opciones)
    if visitante_nuevo:  # 90 días desde la primera visita, como dice la política
        respuesta.set_cookie('_visitor_id', visitante, max_age=DURACION_VISITANTE, **opciones)
    return respuesta
