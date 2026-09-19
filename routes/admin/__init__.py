from flask import Blueprint

from .dashboard import dashboard_bp
from .analiticas import analytics_bp
from .mensajes import messages_bp
from .editar_redes import social_bp
from .editar_seo import seo_bp

# auth_bp es compartido por login.py y cambiar_password.py (antes eran un
# solo auth.py). Se define aquí por el mismo motivo que content_bp más abajo.
auth_bp = Blueprint('auth', __name__, url_prefix='/admin')

# content_bp es compartido por editar_about/editar_blog/editar_carousel/
# editar_servicios/editar_gallery/editar_testimonials/editar_hero (los
# "módulos" del CMS). Antes vivía en routes/content/__init__.py; al eliminar
# esa carpeta, pasa a definirse aquí, en el __init__.py del paquete admin.
content_bp = Blueprint('content', __name__, url_prefix='/admin/contenido')

# Se importan AL FINAL, después de crear auth_bp/content_bp, porque cada uno
# hace `from . import auth_bp` o `from . import content_bp` y registra sus
# rutas con el decorador. Si se importaran antes, esos blueprints todavía no
# existirían (import circular). helpers.py no se importa aquí: no define
# rutas, cada módulo que lo necesita lo importa directamente
# (`from .helpers import ...`).
from . import login, cambiar_password  # noqa: E402,F401
from . import editar_hero, editar_about, editar_carousel, editar_servicios, editar_gallery, editar_testimonials, editar_blog  # noqa: E402,F401


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(social_bp)
    app.register_blueprint(seo_bp)
    app.register_blueprint(content_bp)
