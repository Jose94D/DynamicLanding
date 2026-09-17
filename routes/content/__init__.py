from flask import Blueprint

content_bp = Blueprint('content', __name__, url_prefix='/admin/contenido')

# Los submódulos se importan AL FINAL, después de crear content_bp, porque cada
# uno hace `from . import content_bp` y le registra sus rutas con el decorador.
# Si se importaran antes, content_bp todavía no existiría (import circular).
from . import hero, about, carousel, servicios, gallery, testimonials, blog  # noqa: E402,F401