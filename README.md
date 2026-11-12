<img width="2064" height="512" alt="DynamicLanding_Banner" src="https://github.com/user-attachments/assets/71126984-2098-4889-a87f-ddfca9c8fa28" />

# DynamicLanding

> CMS modular para landing pages comerciales

**DynamicLanding** es un sistema web autogestionable para crear y administrar **landing pages comerciales**. El dueño del sitio edita contenido, orden y visibilidad de las secciones, blog, SEO, redes sociales y analíticas desde un **panel de administración privado**, sin tocar código.

Proyecto fullstack: **API REST en FastAPI**, **panel en React + TypeScript**, **landing renderizada en el servidor** con Tailwind y **MySQL/MariaDB**.

---

## Stack

| Capa | Tecnología | Por qué |
| --- | --- | --- |
| **Backend / API** | Python 3.11+, **FastAPI**, Pydantic | API REST tipada y documentada automáticamente (OpenAPI en `/api/docs`). |
| **ORM y migraciones** | **SQLAlchemy 2**, **Alembic** | Modelos declarativos y esquema versionado. |
| **Base de datos** | **MySQL / MariaDB** (PyMySQL) | Disponible en cualquier hosting cPanel. |
| **Panel admin** | **React 19**, **TypeScript**, **Vite**, **TanStack Query**, React Router | SPA rápida, con caché de datos y actualizaciones optimistas. |
| **Estilos** | **Tailwind CSS 4** | Panel y landing comparten el mismo enfoque de utilidades. |
| **Landing pública** | Jinja2 (renderizado en el servidor) + JS sin dependencias | HTML listo desde el servidor: SEO completo y carga liviana (~38 KB de CSS). |
| **Librerías del panel** | dnd-kit, Quill 2, Chart.js, Bootstrap Icons | Arrastrar y soltar accesible, editor enriquecido y gráficos. |
| **Tests** | pytest + TestClient contra una base MySQL real | Las consultas se prueban con el mismo motor que producción. |

### Arquitectura

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

---

## Funcionalidades

**Panel de administración** (`/admin`)

* **Diseño y visibilidad:** activar/ocultar y reordenar las secciones de la landing arrastrando.
* **Contenidos:** hero, sobre nosotros (con bloques reordenables), carrusel, servicios (con selector de íconos), galería, testimonios y contacto.
* **Blog:** crear, editar, publicar o dejar como borrador, con editor enriquecido y vista previa de borradores.
* **Mensajes** del formulario de contacto, con contador de no leídos.
* **SEO** del sitio y del blog (título, descripción, Open Graph) con validación de largo.
* **Redes sociales:** conexión con la API de Instagram.
* **Analíticas internas:** visitas por semana, mes y año, con gráfico.

**Landing pública**

* Secciones que se renderizan en el orden y con la visibilidad definidos en el panel.
* Carrusel, galería con visor ampliado y testimonios deslizables, sin dependencias de JavaScript externas.
* Blog con archivo agrupado por mes.
* Diseño responsivo y accesible (enlace para saltar al contenido, controles con nombre, respeto a `prefers-reduced-motion`).

**Seguridad**

* Sesión en cookie firmada `httpOnly` y `SameSite=Lax`, renovada en cada login.
* Token **CSRF** obligatorio en todo lo que modifica datos (API y formularios).
* Freno a fuerza bruta en el login (5 intentos por IP cada 15 minutos).
* El HTML del editor se sanea con **bleach** antes de mostrarse.
* Las imágenes subidas se validan de verdad, se redimensionan y se les quitan los metadatos EXIF/GPS.
* El token de Instagram nunca sale de la API: solo se informa si existe.

---

## Estructura del proyecto

```text
DynamicLanding/
├── backend/                    # API + landing (FastAPI)
│   ├── app/
│   │   ├── main.py             # App, middlewares, estáticos y panel en /admin
│   │   ├── config.py           # Configuración desde backend/.env
│   │   ├── db.py, models.py    # SQLAlchemy: conexión y 16 tablas
│   │   ├── schemas.py          # Esquemas Pydantic de la API
│   │   ├── public.py           # Rutas HTML de la landing y el blog
│   │   ├── web.py              # Jinja + helpers (url_for, flash, CSRF)
│   │   ├── imagenes.py         # Optimización de imágenes (Pillow)
│   │   ├── seed.py             # Datos iniciales y usuario admin
│   │   └── api/                # auth, contenido, listas, blog/mensajes/analíticas
│   ├── alembic/                # Migraciones del esquema
│   ├── templates/public/       # Plantillas de la landing (Jinja + Tailwind)
│   ├── static/                 # CSS compilado, JS de la landing y uploads/
│   ├── scripts/                # migrar_desde_sqlite.py
│   └── tests/                  # pytest (API, landing, saneamiento HTML)
│
├── admin/                      # Panel React + TypeScript (Vite)
│   └── src/
│       ├── api.ts              # Cliente de la API (sesión, CSRF, errores)
│       ├── componentes/        # Layout, lista ordenable, editor, selector de íconos…
│       └── paginas/            # Una pantalla por sección del panel
│
├── package.json                # Compila el CSS de la landing (Tailwind CLI)
└── scripts/iniciar_mariadb.ps1 # Arranca la MariaDB de desarrollo (Windows)
```

---

## Modelo de base de datos

<img width="8192" height="2326" alt="ER_model" src="https://github.com/user-attachments/assets/193edd9b-33c4-40e3-9a94-db1eb9a61e91" />
<p align="center">
  <em>Figura 1: Modelo relacional de la base de datos.</em>
</p>

---

## Instalación local

**Requisitos:** Python 3.11+, Node.js 20+ y un servidor MySQL o MariaDB.

### 1. Clonar el repositorio

```bash
git clone https://github.com/Jose94D/DynamicLanding.git
cd DynamicLanding
```

### 2. Crear la base de datos

```sql
CREATE DATABASE dynamiclanding CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dynamiclanding'@'localhost' IDENTIFIED BY 'una-clave-segura';
GRANT ALL PRIVILEGES ON dynamiclanding.* TO 'dynamiclanding'@'localhost';
```

### 3. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env            # Linux/macOS: cp .env.example .env  — y completa los valores
alembic upgrade head              # crea las tablas
python -m app.seed                # datos iniciales + usuario admin
uvicorn app.main:app --reload
```

### 4. Panel de administración

```bash
cd admin
npm install
npm run build                     # FastAPI lo sirve en /admin
```

Para trabajar en el panel con recarga en vivo usa `npm run dev` (http://localhost:5173/admin/): Vite reenvía la API al backend del puerto 8000.

### 5. CSS de la landing

```bash
npm install                       # en la raíz del proyecto
npm run css                       # o npm run css:watch mientras editas plantillas
```

### Accesos

| | URL |
| --- | --- |
| Landing | http://127.0.0.1:8000 |
| Panel admin | http://127.0.0.1:8000/admin |
| Documentación de la API | http://127.0.0.1:8000/api/docs |

---

## Tests

Los tests corren contra una base **aparte** (`<tu base>_test`, se vacía en cada test), nunca contra la de desarrollo:

```sql
CREATE DATABASE dynamiclanding_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON dynamiclanding_test.* TO 'dynamiclanding'@'localhost';
```

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

---

## Estado del proyecto

**En desarrollo.** Migrado de Flask + SQLite + Bootstrap al stack actual; próximos pasos: integración continua y despliegue en hosting cPanel.

---

## Licencia

La información sobre la licencia y las condiciones de uso se incorporará más adelante.
