"""
Consentimiento de cookies analíticas (Ley 21.719).

La decisión vive en la cookie técnica `_consent_status` = "<decision>.<version>.<referencia>":
- decision: 'aceptado' o 'rechazado'
- version: VERSION_POLITICA vigente al decidir. Si la política cambia, se sube la versión y el banner
  vuelve a aparecer, porque el consentimiento se dio sobre otro texto.
- referencia: id aleatorio que también queda en la tabla `consentimientos` (prueba de la decisión).
La cookie es httpOnly: el servidor decide si mostrar el banner, el JavaScript no necesita leerla.
"""
import secrets
from typing import Literal

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from jinja2 import pass_context
from pydantic import BaseModel
from sqlalchemy import delete
from sqlalchemy.orm import Session

from . import models as m
from .config import COOKIE_SECURE
from .db import get_db
from .web import templates, verificar_csrf

VERSION_POLITICA = '2026-11'
COOKIE = '_consent_status'
DURACION_COOKIE = 365 * 24 * 3600  # 1 año
COOKIES_ANALITICAS = ('_session_id', '_visitor_id')
DECISIONES = ('aceptado', 'rechazado')


def decision_vigente(request: Request) -> str | None:
    """'aceptado' / 'rechazado', o None si no ha decidido o decidió sobre una versión anterior de la política."""
    partes = request.cookies.get(COOKIE, '').split('.')
    if len(partes) == 3 and partes[0] in DECISIONES and partes[1] == VERSION_POLITICA:
        return partes[0]
    return None


# En las plantillas: {{ consentimiento() }} -> decide si se muestra el banner.
templates.env.globals['consentimiento'] = pass_context(lambda context: decision_vigente(context['request']))


class Decision(BaseModel):
    decision: Literal['aceptado', 'rechazado']


router = APIRouter(tags=['consentimiento'])


@router.post('/api/consentimiento', status_code=204, dependencies=[Depends(verificar_csrf)],
             summary='Guarda la decisión del banner de cookies (CSRF obligatorio: nadie puede decidir por el visitante)')
def registrar(datos: Decision, request: Request, db: Session = Depends(get_db)):
    retira = datos.decision == 'rechazado' and decision_vigente(request) == 'aceptado'
    return _guardar_decision(db, Response(status_code=204), datos.decision, 'retirado' if retira else datos.decision)


def _guardar_decision(db, respuesta, cookie: str, registro: str):
    """Anota la decisión en `consentimientos` y la deja en la cookie. Al rechazar se borran las cookies analíticas."""
    referencia = secrets.token_hex(16)
    db.add(m.Consentimiento(decision=registro, version=VERSION_POLITICA, referencia=referencia))
    db.commit()
    respuesta.set_cookie(COOKIE, f'{cookie}.{VERSION_POLITICA}.{referencia}', max_age=DURACION_COOKIE,
                         httponly=True, samesite='lax', secure=COOKIE_SECURE)
    if cookie == 'rechazado':
        for nombre in COOKIES_ANALITICAS:
            respuesta.delete_cookie(nombre)
    return respuesta


@router.post('/api/privacidad/eliminar-mis-datos', dependencies=[Depends(verificar_csrf)],
             summary='Borra las analíticas de este navegador y retira el consentimiento (derecho de supresión)')
def eliminar_mis_datos(request: Request, db: Session = Depends(get_db)):
    # El _visitor_id es lo único que une a la persona con sus datos: no guardamos nombres ni IP.
    visitante = request.cookies.get('_visitor_id', '')
    borradas = 0
    if visitante:
        # Los eventos se borran solos con su visita (ON DELETE CASCADE).
        borradas = db.execute(delete(m.AnaliticaSesion).where(m.AnaliticaSesion.visitor_id == visitante)).rowcount
    # Además se retira el consentimiento: borrar sin dejar de medir volvería a juntar datos en la siguiente visita.
    return _guardar_decision(db, JSONResponse({'visitas_eliminadas': borradas}), 'rechazado', 'eliminado')
