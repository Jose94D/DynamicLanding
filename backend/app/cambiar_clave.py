"""
Cambia (o crea) la contraseña de un usuario del panel desde la consola. La clave se escribe
sin mostrarse y no queda en el historial de la terminal.

Uso (desde backend/):
    .venv\\Scripts\\python -m app.cambiar_clave            # usuario 'admin'
    .venv\\Scripts\\python -m app.cambiar_clave otro_usuario
"""
import sys
from getpass import getpass

from sqlalchemy import select
from werkzeug.security import generate_password_hash

from . import models as m
from .db import SessionLocal


def main(argv=sys.argv[1:]):
    usuario = argv[0] if argv else 'admin'
    clave = getpass(f'Nueva contraseña para "{usuario}": ')
    if len(clave) < 8:
        sys.exit('Debe tener al menos 8 caracteres.')
    if clave != getpass('Repítela: '):
        sys.exit('No coinciden.')

    with SessionLocal() as db:
        admin = db.scalar(select(m.Admin).where(m.Admin.username == usuario))
        if admin is None:
            admin = m.Admin(username=usuario)
            db.add(admin)
        admin.password_hash = generate_password_hash(clave)
        db.commit()
    print(f'Listo: ya puedes entrar al panel como "{usuario}".')


if __name__ == '__main__':
    main()
