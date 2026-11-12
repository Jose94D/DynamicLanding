"""Esquemas Pydantic de la API del admin: validan lo que entra y documentan lo que sale (/api/docs)."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Esquema(BaseModel):
    # str_strip_whitespace: quita espacios sobrantes de todos los textos que llegan.
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


# ---------- Auth ----------
class Login(Esquema):
    username: str
    password: str


class CambioPassword(Esquema):
    actual: str
    nueva: str = Field(min_length=8)
    confirmar: str


class Sesion(BaseModel):
    usuario: str | None
    csrf_token: str
    mensajes_no_leidos: int = 0


# ---------- Módulos, bloques y orden ----------
class ModuloOut(Esquema):
    id: str
    nombre_legible: str
    activo: bool
    orden: int


class ModuloEstado(Esquema):
    id: str
    activo: bool
    orden: int


class Visibilidad(Esquema):
    activo: bool


class Orden(Esquema):
    """Nueva secuencia de ids tras un drag & drop; la posición en la lista es el orden."""
    orden: list[int] = Field(min_length=1)


class OrdenSlugs(Esquema):
    orden: list[str] = Field(min_length=1)


# ---------- Contenido de una sola fila ----------
class Hero(Esquema):
    titulo: str = Field(min_length=1)
    subtitulo: str | None = None
    texto_boton: str | None = None
    url_boton: str | None = None


class AboutOut(Esquema):
    titulo: str
    descripcion: str | None
    mision: str | None
    nombre_archivo: str | None
    bloques: list[ModuloOut]


class ContactDatos(Esquema):
    titulo: str = Field(min_length=1)
    subtitulo: str | None = None
    telefono: str | None = None
    email: str | None = None
    ubicacion_texto: str | None = None
    horario: str | None = None


class SubmoduloVisible(Esquema):
    id: str
    activo: bool


class ContactoIn(Esquema):
    datos: ContactDatos
    direccion: str
    submodulos: list[SubmoduloVisible] = []


class ContactoOut(Esquema):
    datos: ContactDatos
    direccion: str
    submodulos: list[ModuloOut]


class Seo(Esquema):
    meta_titulo: str = Field(min_length=1, max_length=60)
    meta_descripcion: str = Field(min_length=1, max_length=160)
    og_image: str | None = None


class RedIn(Esquema):
    access_token: str | None = Field(None, description='Omitir o null para conservar el token guardado.')
    account_id: str = ''
    activo_api: bool


class RedOut(Esquema):
    plataforma: str
    account_id: str | None
    activo_api: bool
    tiene_token: bool  # el token nunca sale de la API; solo se indica si existe


# ---------- Listas ordenables ----------
class ImagenOut(Esquema):
    id: int
    nombre_archivo: str
    orden: int


class GaleriaOut(ImagenOut):
    titulo: str | None


class ServicioIn(Esquema):
    icono: str = 'bi-star'
    titulo: str = Field(min_length=1)
    descripcion: str = Field(min_length=1)


class ServicioOut(ServicioIn):
    id: int
    orden: int


class TestimonioOut(Esquema):
    id: int
    nombre: str
    cargo: str | None
    texto: str
    foto: str | None
    calificacion: int
    orden: int


# ---------- Blog, mensajes, analíticas ----------
class ArticuloIn(Esquema):
    titulo: str = Field(min_length=1)
    extracto: str = Field(min_length=1)
    contenido: str = Field(min_length=1)
    activo: bool = True


class ArticuloResumen(Esquema):
    id: int
    titulo: str
    slug: str
    extracto: str
    fecha_publicacion: datetime | None
    activo: bool


class ArticuloOut(ArticuloResumen):
    contenido: str


class MensajeOut(Esquema):
    id: int
    nombre: str
    email: str
    mensaje: str
    fecha_envio: datetime
    leido: bool


class MensajesOut(BaseModel):
    mensajes: list[MensajeOut]
    no_leidos: int


class Serie(BaseModel):
    periodo: str
    total: int


class AnaliticasOut(BaseModel):
    total: int
    anio_actual: int
    mes_actual: int
    semana_actual: int
    por_anio: list[Serie]
    por_mes: list[Serie]
    por_semana: list[Serie]
