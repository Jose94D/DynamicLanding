import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent
load_dotenv(BACKEND_DIR / '.env')  # no pisa variables ya definidas en el entorno (útil en tests y en cPanel)

TEMPLATES_DIR = BACKEND_DIR / 'templates'
STATIC_DIR = BACKEND_DIR / 'static'
# Configurable para que los tests no escriban en las imágenes reales.
UPLOADS_DIR = Path(os.environ.get('UPLOADS_DIR', STATIC_DIR / 'uploads'))
MAX_SUBIDA_MB = 10
# Panel admin compilado (npm run build en admin/).
ADMIN_DIST = PROJECT_DIR / 'admin' / 'dist'

DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    raise RuntimeError(
        'Falta DATABASE_URL. Defínela en backend/.env, por ejemplo:\n'
        '  DATABASE_URL=mysql+pymysql://usuario:clave@127.0.0.1:3306/base?charset=utf8mb4'
    )

SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = secrets.token_hex(32)
    print(
        '\n⚠️  ADVERTENCIA: no definiste SECRET_KEY. Se generó una temporal que cambia en cada\n'
        '    reinicio (cierra las sesiones activas). Defínela en backend/.env antes de producción.\n'
    )

# Con COOKIE_SECURE=1 la cookie de sesión solo viaja por HTTPS. Apagado por defecto para desarrollo local (http).
COOKIE_SECURE = os.environ.get('COOKIE_SECURE', '0') == '1'
