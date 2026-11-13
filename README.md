<p align="center">
  <img width="2064" height="512" alt="DynamicLanding, CMS modular para landing pages comerciales" src="https://github.com/user-attachments/assets/71126984-2098-4889-a87f-ddfca9c8fa28" />
</p>

**DynamicLanding** es un CMS modular para **landing pages comerciales**. El dueño del sitio edita el contenido, el orden y la visibilidad de las secciones, el blog, el SEO, las redes sociales, la privacidad y las analíticas desde un **panel de administración privado**, sin tocar código. La API está hecha en **FastAPI**, el panel en **React + TypeScript** y la landing se renderiza en el servidor con Tailwind sobre **MySQL/MariaDB**.

> **Estado:** en desarrollo. Migrado de Flask + SQLite + Bootstrap al stack actual; faltan la integración continua y el despliegue en hosting cPanel.

## Capturas

<!-- Las capturas van en docs/capturas/ en pares de 420px, igual que en GunplaScrapper-Chile. Ejemplo:
<p align="center">
  <img src="docs/capturas/landing.png" width="420" alt="Landing pública" />
  <img src="docs/capturas/blog.png" width="420" alt="Blog" />
</p>
-->

* **Landing:** las secciones aparecen en el orden y con la visibilidad que se definen en el panel.
* **Blog:** archivo agrupado por mes y artículos con su propio SEO.
* **Privacidad:** banner de cookies y política de privacidad editable.

### Panel de administración

* **Acceso:** login con freno a fuerza bruta.
* **Diseño:** activar, ocultar y reordenar las secciones arrastrando.
* **Contenidos:** hero, sobre nosotros (bloques reordenables), carrusel, servicios (selector de íconos), galería, testimonios y contacto.
* **Blog:** crear, editar, publicar o dejar como borrador, con editor enriquecido y vista previa.
* **Mensajes:** formulario de contacto con contador de no leídos.
* **SEO:** título, descripción y Open Graph del sitio y del blog, con validación de largo.
* **Redes:** conexión con la API de Instagram.
* **Privacidad:** textos legales y versión de la política.
* **Analíticas:**
  * Visitas por semana, mes y año, con gráfico y comparativas.
  * Sesiones, eventos, dispositivo, navegador y origen del tráfico (solo con consentimiento).
* **Cuenta:** cambio de contraseña.

## Funciones

**Ya funcionan:**

* Landing modular renderizada en el servidor, con carrusel, galería con visor ampliado y testimonios deslizables sin dependencias de JavaScript externas.
* Diseño responsivo y accesible: enlace para saltar al contenido, controles con nombre y respeto a `prefers-reduced-motion`.
* Panel React con caché de datos y actualizaciones optimistas.
* Consentimiento de cookies y retención de datos según la Ley 21.719.

**Próximos pasos:** integración continua y despliegue en hosting cPanel.

## Seguridad

* Sesión en cookie firmada `httpOnly` y `SameSite=Lax`, renovada en cada login.
* Token **CSRF** obligatorio en todo lo que modifica datos (API y formularios).
* Freno a fuerza bruta en el login (5 intentos por IP cada 15 minutos).
* El HTML del editor se sanea con **bleach** antes de mostrarse.
* Las imágenes subidas se validan de verdad, se redimensionan y se les quitan los metadatos EXIF/GPS.
* El token de Instagram nunca sale de la API: solo se informa si existe.
* Las analíticas detalladas solo se registran si el visitante acepta las cookies; los ids de sesión y visitante son `httpOnly`.

## Tecnología

| Pieza | Elección |
| --- | --- |
| Backend / API | Python 3.11+, **FastAPI**, Pydantic (OpenAPI en `/api/docs`) |
| ORM y migraciones | **SQLAlchemy 2**, **Alembic** |
| Base de datos | **MySQL / MariaDB** (PyMySQL), disponible en cualquier hosting cPanel |
| Panel admin | **React 19**, **TypeScript**, **Vite**, **TanStack Query**, React Router |
| Estilos | **Tailwind CSS 4** en el panel y en la landing |
| Landing pública | Jinja2 renderizado en el servidor + JS sin dependencias |
| Librerías del panel | dnd-kit, Quill 2, Chart.js, Bootstrap Icons |
| Tests | pytest + TestClient contra una base MySQL real |

```text
                 ┌───────────────────────────── FastAPI ─────────────────────────────┐
 Visitante  ───► │  /, /blog, /articulo/{id}   → plantillas Jinja + Tailwind (SSR)   │
                 │  POST /contacto             → formulario con CSRF y honeypot      │
                 │                                                                   │ ──► MySQL / MariaDB
 Admin      ───► │  /admin/*                   → SPA React (archivos compilados)     │      (SQLAlchemy)
 (navegador)     │  /api/auth/*, /api/admin/*  → API REST JSON (sesión + CSRF)       │
                 │  /static/uploads/*          → imágenes optimizadas con Pillow     │
                 └───────────────────────────────────────────────────────────────────┘
```

### Base de datos

```mermaid
erDiagram
    analiticas_sesiones ||--o{ analiticas_eventos : "tiene"

    admin {
        int id PK
        varchar username UK
        varchar password_hash
    }
    modulos {
        varchar id PK "slug = plantilla modulos/<id>.html"
        varchar nombre_legible
        bool activo
        int orden
    }
    contenido_hero {
        int id PK "fila única"
        text titulo
        text subtitulo
        text texto_boton
        text url_boton
    }
    contenido_about {
        int id PK "fila única"
        text titulo
        text descripcion
        text mision
        varchar nombre_archivo
    }
    contenido_about_bloques {
        varchar id PK
        varchar nombre_legible
        bool activo
        int orden
    }
    contenido_carousel {
        int id PK
        varchar nombre_archivo
        int orden
    }
    contenido_services {
        int id PK
        varchar icono
        text titulo
        text descripcion
        int orden
    }
    contenido_gallery {
        int id PK
        varchar nombre_archivo
        text titulo
        int orden
    }
    contenido_testimonials {
        int id PK
        text nombre
        text cargo
        text texto
        varchar foto
        int calificacion "1 a 5"
        int orden
    }
    contenido_blog {
        int id PK
        text titulo
        varchar slug UK
        text extracto
        longtext contenido
        varchar imagen_portada
        datetime fecha_publicacion
        bool activo
    }
    contenido_contact_submodulos {
        varchar id PK
        varchar nombre_legible
        bool activo
        int orden
    }
    contenido_contact_datos {
        int id PK "fila única"
        text titulo
        text subtitulo
        text telefono
        text email
        text ubicacion_texto
        text horario
    }
    contenido_contact_mapa {
        int id PK "fila única"
        text direccion
    }
    configuracion_seo {
        int id PK "fila única"
        text meta_titulo
        text meta_descripcion
        varchar og_image
    }
    configuracion_seo_blog {
        int id PK "fila única"
        text meta_titulo
        text meta_descripcion
        varchar og_image
    }
    configuracion_legal {
        int id PK "fila única"
        text razon_social
        varchar rut
        varchar email_privacidad
    }
    configuracion_redes {
        int id PK
        varchar plataforma UK
        text access_token
        varchar account_id
        bool activo_api
    }
    consentimientos {
        int id PK
        datetime fecha
        varchar decision "aceptado / rechazado / retirado"
        varchar version
        varchar referencia "también va en la cookie"
    }
    analiticas_visitas {
        int id PK
        datetime fecha
        varchar ruta
    }
    analiticas_sesiones {
        varchar session_id PK
        varchar visitor_id
        datetime inicio
        datetime ultima_actividad
        int segundos_activos
        varchar dispositivo
        varchar navegador
        varchar sistema
        varchar origen
        varchar referente
        varchar utm_source
        varchar utm_medium
        varchar utm_campaign
    }
    analiticas_eventos {
        int id PK
        varchar session_id FK
        datetime fecha
        varchar tipo
        varchar ruta
    }
    mensajes_contacto {
        int id PK
        text nombre
        varchar email
        text mensaje
        datetime fecha_envio
        bool leido
    }
```

* `contenido_*`: una tabla por sección de la landing; `modulos` guarda su orden y visibilidad.
* `configuracion_*`: SEO, SEO del blog, textos legales y redes sociales.
* `analiticas_visitas` cuenta visitas anónimas sin cookies; `analiticas_sesiones` y `analiticas_eventos` solo se llenan con consentimiento, que queda registrado en `consentimientos`.
* `mensajes_contacto` y `admin` completan el esquema.
* La única clave foránea es `analiticas_eventos.session_id` (con `ON DELETE CASCADE`); las tablas marcadas "fila única" tienen siempre `id = 1`.

## Ejecutar

Requisitos: Python 3.11+, Node.js 20+ y un servidor MySQL o MariaDB.

```bash
git clone https://github.com/Jose94D/DynamicLanding.git
cd DynamicLanding
```

Crea la base de datos:

```sql
CREATE DATABASE dynamiclanding CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dynamiclanding'@'localhost' IDENTIFIED BY 'una-clave-segura';
GRANT ALL PRIVILEGES ON dynamiclanding.* TO 'dynamiclanding'@'localhost';
```

Backend (en Linux/macOS usa `source .venv/bin/activate` y `cp`):

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

`backend/.env`:

```env
DATABASE_URL=mysql+pymysql://usuario:clave@127.0.0.1:3306/dynamiclanding?charset=utf8mb4
SECRET_KEY=
```

| Variable | Por defecto | Uso |
| --- | --- | --- |
| `SECRET_KEY` | aleatoria en cada arranque | Firma la cookie de sesión. Genérala con `python -c "import secrets; print(secrets.token_hex(32))"`. |
| `COOKIE_SECURE` | `0` | Con `1` la cookie de sesión solo viaja por HTTPS (actívalo en producción). |
| `ADMIN_USERNAME` | `admin` | Usuario que crea `python -m app.seed` si no existe ninguno. |
| `ADMIN_PASSWORD` | aleatoria | Si falta, se genera y se muestra una sola vez en consola. |
| `UPLOADS_DIR` | `backend/static/uploads` | Carpeta de imágenes subidas. |

Panel de administración (FastAPI lo sirve en `/admin`):

```bash
cd admin
npm install
npm run build
```

Para trabajar en el panel con recarga en vivo usa `npm run dev` (http://localhost:5173/admin/): Vite reenvía la API al backend del puerto 8000.

CSS de la landing, desde la raíz del proyecto (`npm run css:watch` mientras editas plantillas):

```bash
npm install
npm run css
```

Cambiar la contraseña de un usuario del panel (desde `backend/`):

```bash
python -m app.cambiar_clave
```

| | URL |
| --- | --- |
| Landing | http://127.0.0.1:8000 |
| Panel admin | http://127.0.0.1:8000/admin |
| Documentación de la API | http://127.0.0.1:8000/api/docs |

> `python -m app.retencion` (desde `backend/`) borra las analíticas con más de 13 meses y los mensajes de contacto con más de 24, como promete la política de privacidad. En producción se programa una vez al día con un cron de cPanel.

### MariaDB como servicio (Windows, opcional)

`scripts/crear_servicio_mariadb.ps1` crea una MariaDB propia del proyecto como servicio (puerto 3307, datos en `C:\ProgramData\DynamicLanding`): arranca sola con Windows y se apaga en orden al apagar el equipo. Toma usuario y clave de `backend/.env` e importa el respaldo más reciente de `respaldos/*.sql`. Desde la raíz del proyecto, en una PowerShell **como administrador**:

```bash
powershell -ExecutionPolicy Bypass -File scripts\crear_servicio_mariadb.ps1
```

Después, `scripts/iniciar_mariadb.ps1` (lo que corre VS Code antes de F5) solo comprueba que el servicio esté arriba.

### Tests

Corren contra una base **aparte** (`<tu base>_test`, se vacía en cada test), nunca contra la de desarrollo:

```sql
CREATE DATABASE dynamiclanding_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON dynamiclanding_test.* TO 'dynamiclanding'@'localhost';
```

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

## Estructura

```text
DynamicLanding/
├── backend/                    # API + landing (FastAPI)
│   ├── app/
│   │   ├── main.py             # App, middlewares, estáticos y panel en /admin
│   │   ├── config.py           # Configuración desde backend/.env
│   │   ├── db.py, models.py    # SQLAlchemy: conexión y tablas
│   │   ├── schemas.py          # Esquemas Pydantic de la API
│   │   ├── public.py           # Rutas HTML de la landing y el blog
│   │   ├── web.py              # Jinja + helpers (url_for, flash, CSRF)
│   │   ├── analiticas.py       # Eventos de analíticas con consentimiento
│   │   ├── clasificar.py       # Dispositivo, navegador, origen y bots
│   │   ├── consentimiento.py   # Banner de cookies (Ley 21.719)
│   │   ├── retencion.py        # Borrado de datos antiguos
│   │   ├── cambiar_clave.py    # Cambio de contraseña por consola
│   │   ├── imagenes.py         # Optimización de imágenes (Pillow)
│   │   ├── seed.py             # Datos iniciales y usuario admin
│   │   └── api/                # auth, contenido, listas, blog, mensajes, métricas
│   ├── alembic/                # Migraciones del esquema
│   ├── templates/public/       # Plantillas de la landing (Jinja + Tailwind)
│   ├── static/                 # CSS compilado, JS de la landing y uploads/
│   ├── scripts/                # migrar_desde_sqlite.py
│   └── tests/                  # pytest
│
├── admin/                      # Panel React + TypeScript (Vite)
│   └── src/
│       ├── api.ts              # Cliente de la API (sesión, CSRF, errores)
│       ├── componentes/        # Layout, lista ordenable, editor, selector de íconos…
│       └── paginas/            # Una pantalla por sección del panel
│
├── package.json                # Compila el CSS de la landing (Tailwind CLI)
└── scripts/                    # MariaDB de desarrollo (Windows)
```

## Licencia

La información sobre la licencia y las condiciones de uso se incorporará más adelante.
