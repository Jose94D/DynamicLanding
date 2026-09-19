from .public import public_bp


def register_blueprints(app):
    app.register_blueprint(public_bp)
