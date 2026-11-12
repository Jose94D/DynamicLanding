import re
import unicodedata

import bleach
from markupsafe import Markup


def generar_slug(texto):
    """Convierte un título en un slug URL-friendly (ej: 'Mi Post!' -> 'mi-post')."""
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    texto = re.sub(r'[^\w\s-]', '', texto).strip().lower()
    return re.sub(r'[\s_-]+', '-', texto)


# ==========================================
# LIMPIEZA DE HTML (contenido de los editores Quill)
# Lista blanca con lo que generan las barras de herramientas del admin:
# negrita/cursiva/subrayado, títulos, listas, citas, enlaces e imágenes.
# Todo lo demás (<script>, onclick=, javascript:, <iframe>, style=...) se elimina.
# ==========================================
ETIQUETAS_PERMITIDAS = {
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 's', 'span',
    'h2', 'h3', 'ul', 'ol', 'li', 'blockquote', 'a', 'img',
}
IMAGEN_DATA_URI = re.compile(r'^data:image/(png|jpe?g|gif|webp);base64,', re.I)


def _atributo_permitido(etiqueta, nombre, valor):
    if nombre == 'class':
        return valor.startswith('ql-')  # solo clases propias de Quill (alineación, sangría)
    if etiqueta == 'a':
        if nombre == 'href':
            return valor.startswith(('http://', 'https://', 'mailto:', 'tel:', '/', '#'))
        return nombre in ('target', 'rel', 'title')
    if etiqueta == 'img':
        if nombre == 'src':
            # Quill incrusta las imágenes como data URI; solo aceptamos formatos raster.
            return valor.startswith(('http://', 'https://', '/')) or bool(IMAGEN_DATA_URI.match(valor))
        return nombre in ('alt', 'title', 'width', 'height')
    return False


def limpiar_html(html):
    """Filtro Jinja: devuelve el HTML ya saneado y marcado como seguro (reemplaza a |safe)."""
    if not html:
        return ''
    limpio = bleach.clean(
        html,
        tags=ETIQUETAS_PERMITIDAS,
        attributes=_atributo_permitido,
        protocols={'http', 'https', 'mailto', 'tel', 'data'},
        strip=True,
    )
    return Markup(limpio)
