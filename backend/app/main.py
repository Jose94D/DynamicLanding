from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import OperationalError
from starlette.middleware.sessions import SessionMiddleware

from . import analiticas, consentimiento, public
from .api import auth, blog, contenido, listas, metricas
from .config import ADMIN_DIST, COOKIE_SECURE, MAX_SUBIDA_MB, SECRET_KEY, STATIC_DIR

app = FastAPI(title='DynamicLanding API', docs_url='/api/docs', redoc_url=None, openapi_url='/api/openapi.json')


@app.exception_handler(OperationalError)
async def base_no_disponible(request: Request, exc: OperationalError):
    """Sin conexión a MySQL: mensaje claro en vez de un 500 con traza. El detalle queda en la consola."""
    print(f'⚠️  Error de base de datos: {exc.orig}')
    return PlainTextResponse(
        'No se pudo conectar a la base de datos. En desarrollo: powershell -File scripts\\iniciar_mariadb.ps1',
        status_code=503,
    )


@app.middleware('http')
async def limitar_tamano(request: Request, call_next):
    """Tope por request (subidas incluidas): un archivo gigante no debe llenar la memoria ni el disco.
    shortcut: solo mira Content-Length; en el hosting reforzar con LimitRequestBody de Apache."""
    if int(request.headers.get('content-length') or 0) > MAX_SUBIDA_MB * 1024 * 1024:
        return JSONResponse({'detail': f'El archivo es demasiado grande. Máximo {MAX_SUBIDA_MB} MB.'}, status_code=413)
    return await call_next(request)


# Cookie con nombre propio: las cookies se comparten entre puertos del mismo host, así no choca con otra app local que use 'session'.
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie='dl_session',
    same_site='lax',
    https_only=COOKIE_SECURE,
)
app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')
for modulo in (auth, contenido, listas, blog, metricas, consentimiento, analiticas, public):
    app.include_router(modulo.router)


@app.get('/admin', include_in_schema=False)
def admin_sin_barra():
    return RedirectResponse('/admin/')


@app.get('/admin/{ruta:path}', include_in_schema=False)
def panel_admin(ruta: str):
    """Sirve el panel React. Cualquier ruta que no sea un archivo devuelve index.html (el router de React decide)."""
    archivo = (ADMIN_DIST / ruta).resolve()
    if ruta and archivo.is_file() and ADMIN_DIST.resolve() in archivo.parents:  # sin salir de dist/ (../)
        return FileResponse(archivo)
    indice = ADMIN_DIST / 'index.html'
    if not indice.is_file():
        return PlainTextResponse('Panel no compilado: ejecuta "npm run build" en admin/.', status_code=503)
    return FileResponse(indice)
