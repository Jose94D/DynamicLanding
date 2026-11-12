"""Se ejecuta con `pytest` o directamente: `python tests/test_limpiar_html.py`."""

from app.utils import limpiar_html  # noqa: E402


def test_conserva_formato_de_quill():
    html = '<h2>T</h2><p class="ql-align-center"><strong>b</strong></p><a href="https://x.cl" target="_blank">l</a>'
    assert limpiar_html(html) == html


def test_conserva_imagen_incrustada():
    html = '<img src="data:image/png;base64,iVBORw0KGgo=">'
    assert limpiar_html(html) == html


def test_elimina_html_peligroso():
    peligrosos = [
        '<script>alert(1)</script>',
        '<img src="/x.png" onerror="alert(1)">',
        '<a href="javascript:alert(1)">x</a>',
        '<a href="JaVaScRiPt:alert(1)">x</a>',
        '<a href="data:text/html,hola">x</a>',
        '<img src="data:image/svg+xml;base64,PHN2Zz4=">',
        '<iframe src="https://evil"></iframe>',
        '<p style="position:fixed">p</p>',
    ]
    for html in peligrosos:
        limpio = str(limpiar_html(html)).lower()
        for prohibido in ('<script', 'onerror', 'javascript:', 'data:text', 'svg', '<iframe', 'style='):
            assert prohibido not in limpio, (html, limpio)


if __name__ == '__main__':
    test_conserva_formato_de_quill()
    test_conserva_imagen_incrustada()
    test_elimina_html_peligroso()
    print('OK')
