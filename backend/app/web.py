"""
Plantillas Jinja + los helpers estilo Flask que usan (url_for, flash, csrf_input),
para reutilizar las plantillas públicas existentes sin reescribirlas.
"""
import hmac
import secrets

from fastapi import HTTPException, Request
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context
from markupsafe import Markup

from .config import TEMPLATES_DIR
from .utils import limpiar_html

templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.filters['limpiar_html'] = limpiar_html


@pass_context
def _url_for(context, name, **params):
    """url_for con la firma de Flask: url_for('static', filename=...) y url_for('public.index')."""
    request = context['request']
    if name == 'static':
        params = {'path': params.pop('filename')}
    # Ruta relativa (no absoluta): detrás del proxy de cPanel, una URL absoluta podría salir en http://.
    return request.scope.get('root_path', '') + request.app.url_path_for(name, **params)


def flash(request: Request, mensaje: str, categoria: str = 'info'):
    request.session.setdefault('_flashes', []).append([categoria, mensaje])


@pass_context
def _get_flashed_messages(context, with_categories=False):
    mensajes = context['request'].session.pop('_flashes', [])
    return [tuple(m) for m in mensajes] if with_categories else [m[1] for m in mensajes]


def csrf_token(request: Request) -> str:
    if '_csrf' not in request.session:
        request.session['_csrf'] = secrets.token_hex(32)
    return request.session['_csrf']


@pass_context
def _csrf_input(context):
    return Markup(f'<input type="hidden" name="csrf_token" value="{csrf_token(context["request"])}">')


async def verificar_csrf(request: Request):
    """Dependencia para requests que modifican datos: el token debe venir en el header 'X-CSRFToken'
    (API del admin) o en el campo 'csrf_token' (formularios HTML). GET/HEAD/OPTIONS no lo necesitan."""
    if request.method in ('GET', 'HEAD', 'OPTIONS'):
        return
    esperado = request.session.get('_csrf')
    enviado = request.headers.get('X-CSRFToken') or (await request.form()).get('csrf_token') or ''
    if not esperado or not hmac.compare_digest(str(enviado), esperado):
        raise HTTPException(400, 'Token de seguridad inválido o vencido. Recarga la página e inténtalo de nuevo.')


templates.env.globals.update(
    url_for=_url_for,
    get_flashed_messages=_get_flashed_messages,
    csrf_input=_csrf_input,
)
