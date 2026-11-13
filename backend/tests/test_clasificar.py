import pytest

from app.clasificar import clasificar_navegador, clasificar_origen, dominio, es_bot

UA = {
    'chrome_win': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36',
    'edge_win': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36 Edg/131.0',
    'safari_iphone': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1',
    'chrome_android': 'Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Mobile Safari/537.36',
    'samsung_tablet': 'Mozilla/5.0 (Linux; Android 13; SM-X200) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/26.0 Chrome/122.0 Safari/537.36',
    'firefox_mac': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14.5; rv:132.0) Gecko/20100101 Firefox/132.0',
    'safari_ipad': 'Mozilla/5.0 (iPad; CPU OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
}


@pytest.mark.parametrize('clave, esperado', [
    ('chrome_win', ('escritorio', 'Chrome', 'Windows')),
    ('edge_win', ('escritorio', 'Edge', 'Windows')),
    ('safari_iphone', ('movil', 'Safari', 'iOS')),
    ('chrome_android', ('movil', 'Chrome', 'Android')),
    ('samsung_tablet', ('tablet', 'Samsung Internet', 'Android')),
    ('firefox_mac', ('escritorio', 'Firefox', 'macOS')),
    ('safari_ipad', ('tablet', 'Safari', 'iOS')),
])
def test_clasificar_navegador(clave, esperado):
    assert clasificar_navegador(UA[clave]) == esperado


def test_navegador_desconocido():
    assert clasificar_navegador(None) == ('escritorio', 'Otro', 'Otro')


@pytest.mark.parametrize('ua, bot', [
    ('Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)', True),
    ('Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 HeadlessChrome/120.0', True),
    ('curl/8.4.0', True),
    ('', True),
    (UA['chrome_win'], False),
])
def test_es_bot(ua, bot):
    assert es_bot(ua) is bot


@pytest.mark.parametrize('referente, utm, esperado', [
    (None, False, 'directo'),
    ('https://misitio.cl/blog', False, 'directo'),          # navegación interna
    ('https://www.google.cl/', False, 'buscador'),
    ('https://duckduckgo.com/', False, 'buscador'),
    ('https://l.instagram.com/?u=x', False, 'social'),
    ('https://t.co/abc', False, 'social'),
    ('https://otroblog.com/articulo', False, 'referido'),
    ('https://www.google.cl/', True, 'campaña'),           # los UTM mandan
    ('https://notgoogle.com/', False, 'referido'),          # 'google' dentro de otro dominio no cuenta
])
def test_clasificar_origen(referente, utm, esperado):
    assert clasificar_origen(referente, 'misitio.cl:8000', utm) == esperado


def test_dominio_no_guarda_la_ruta():
    assert dominio('https://www.ejemplo.com/perfil?email=ana@x.cl') == 'ejemplo.com'
