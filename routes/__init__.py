from .admin import register_blueprints as register_admin_blueprints
from .public import register_blueprints as register_public_blueprints


def register_blueprints(app):
    register_admin_blueprints(app)
    register_public_blueprints(app)
