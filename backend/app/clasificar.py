"""
Clasificación simple para las analíticas: dispositivo/navegador/sistema desde el User-Agent, origen del
tráfico desde el referente y los UTM, y detección de bots. Sin dependencias: para estas categorías
gruesas bastan unas reglas; una librería de user-agents sería más peso que beneficio.
"""
import re
from urllib.parse import urlparse

_BOT = re.compile(r'bot|crawl|spider|slurp|facebookexternalhit|preview|headless|lighthouse|python-requests|curl|wget|httpx|scrapy',
                  re.I)

# (regex, nombre) en orden: varios navegadores incluyen "Chrome" o "Safari" en su User-Agent.
_NAVEGADORES = [
    (r'Edg(e|A|iOS)?/', 'Edge'), (r'OPR/|Opera', 'Opera'), (r'SamsungBrowser', 'Samsung Internet'),
    (r'Firefox/|FxiOS', 'Firefox'), (r'Chrome/|CriOS', 'Chrome'), (r'Safari/', 'Safari'),
]
_SISTEMAS = [
    (r'Windows', 'Windows'), (r'iPhone|iPad|iPod', 'iOS'), (r'Android', 'Android'), (r'CrOS', 'ChromeOS'),
    (r'Mac OS X|Macintosh', 'macOS'), (r'Linux', 'Linux'),
]

_BUSCADORES = re.compile(r'(^|\.)(google\.[a-z.]+|bing\.com|duckduckgo\.com|yahoo\.[a-z.]+|ecosia\.org|yandex\.[a-z.]+|'
                         r'baidu\.com|search\.brave\.com)$')
_REDES = re.compile(r'(^|\.)(facebook\.com|fb\.com|instagram\.com|t\.co|twitter\.com|x\.com|linkedin\.com|lnkd\.in|'
                    r'tiktok\.com|youtube\.com|pinterest\.[a-z.]+|reddit\.com|whatsapp\.com|wa\.me|threads\.net)$')


def es_bot(user_agent: str | None) -> bool:
    return not user_agent or bool(_BOT.search(user_agent))


def _primero(reglas, texto, defecto='Otro'):
    return next((nombre for patron, nombre in reglas if re.search(patron, texto)), defecto)


def clasificar_navegador(user_agent: str | None) -> tuple[str, str, str]:
    """(dispositivo, navegador, sistema). Dispositivo: 'movil', 'tablet' o 'escritorio'."""
    ua = user_agent or ''
    if re.search(r'iPad|Tablet', ua) or ('Android' in ua and 'Mobile' not in ua):
        dispositivo = 'tablet'
    elif re.search(r'Mobi|iPhone|iPod|Android', ua):
        dispositivo = 'movil'
    else:
        dispositivo = 'escritorio'
    return dispositivo, _primero(_NAVEGADORES, ua), _primero(_SISTEMAS, ua)


def dominio(url: str | None) -> str | None:
    """Solo el dominio, sin 'www.': nunca se guarda la URL completa (podría traer datos personales)."""
    host = (urlparse(url).hostname or '') if url else ''
    return host.removeprefix('www.')[:255] or None


def clasificar_origen(referente: str | None, host_propio: str, hay_utm: bool) -> str:
    """'campaña' (trae UTM), 'buscador', 'social', 'referido' o 'directo' (sin referente o desde el mismo sitio)."""
    if hay_utm:
        return 'campaña'
    host = dominio(referente)
    if not host or host == host_propio.split(':')[0].removeprefix('www.'):
        return 'directo'
    if _BUSCADORES.search(host):
        return 'buscador'
    if _REDES.search(host):
        return 'social'
    return 'referido'
