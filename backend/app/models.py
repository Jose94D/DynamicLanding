"""
Modelos SQLAlchemy: mismas tablas y columnas que el database.py original (SQLite),
adaptadas a MySQL/MariaDB:
- Columnas con UNIQUE o PRIMARY KEY de texto usan String(n): MySQL no indexa TEXT sin largo.
- El contenido del blog usa LONGTEXT: Quill incrusta imágenes en base64 y TEXT (64 KB) se queda corto.
- Los valores por defecto de columnas TEXT van del lado de Python (default=), no del servidor.
"""
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base

TextoLargo = Text().with_variant(LONGTEXT(), 'mysql', 'mariadb')


def _singleton(tabla):
    """Tablas de una sola fila: id siempre = 1."""
    return (CheckConstraint('id = 1', name=f'ck_{tabla}_singleton'),)


# ==========================================================
# ADMINISTRACIÓN
# ==========================================================
class Admin(Base):
    __tablename__ = 'admin'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))


# ==========================================================
# MÓDULOS DE LA LANDING (visibilidad + orden)
# 'id' es un slug que además es el nombre del include en templates/public/modulos/<id>.html
# ==========================================================
class Modulo(Base):
    __tablename__ = 'modulos'
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    nombre_legible: Mapped[str] = mapped_column(String(150))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    orden: Mapped[int] = mapped_column(Integer)


# ==========================================================
# CONTENIDO POR MÓDULO
# ==========================================================
class ContenidoHero(Base):
    __tablename__ = 'contenido_hero'
    __table_args__ = _singleton('contenido_hero')
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    titulo: Mapped[str] = mapped_column(Text)
    subtitulo: Mapped[str | None] = mapped_column(Text)
    texto_boton: Mapped[str | None] = mapped_column(Text)
    url_boton: Mapped[str | None] = mapped_column(Text)


class ContenidoAbout(Base):
    __tablename__ = 'contenido_about'
    __table_args__ = _singleton('contenido_about')
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    titulo: Mapped[str] = mapped_column(Text)
    descripcion: Mapped[str | None] = mapped_column(Text)
    mision: Mapped[str | None] = mapped_column(Text)
    nombre_archivo: Mapped[str | None] = mapped_column(String(255))


class ContenidoAboutBloque(Base):
    """Orden/visibilidad de los bloques internos de 'about' (historia / misión / imagen)."""
    __tablename__ = 'contenido_about_bloques'
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    nombre_legible: Mapped[str] = mapped_column(String(150))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    orden: Mapped[int] = mapped_column(Integer)


class ContenidoCarousel(Base):
    __tablename__ = 'contenido_carousel'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_archivo: Mapped[str] = mapped_column(String(255))
    orden: Mapped[int] = mapped_column(Integer, default=1)


class ContenidoService(Base):
    __tablename__ = 'contenido_services'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    icono: Mapped[str] = mapped_column(String(100), default='bi-star')
    titulo: Mapped[str] = mapped_column(Text)
    descripcion: Mapped[str] = mapped_column(Text)
    orden: Mapped[int] = mapped_column(Integer, default=1)


class ContenidoGallery(Base):
    __tablename__ = 'contenido_gallery'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_archivo: Mapped[str] = mapped_column(String(255))
    titulo: Mapped[str | None] = mapped_column(Text)
    orden: Mapped[int] = mapped_column(Integer, default=1)


class ContenidoTestimonial(Base):
    __tablename__ = 'contenido_testimonials'
    __table_args__ = (CheckConstraint('calificacion BETWEEN 1 AND 5', name='ck_testimonials_calificacion'),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(Text)
    cargo: Mapped[str | None] = mapped_column(Text)
    texto: Mapped[str] = mapped_column(Text)
    foto: Mapped[str | None] = mapped_column(String(255))
    calificacion: Mapped[int] = mapped_column(Integer, default=5)
    orden: Mapped[int] = mapped_column(Integer, default=1)


class ContenidoBlog(Base):
    __tablename__ = 'contenido_blog'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    titulo: Mapped[str] = mapped_column(Text)
    slug: Mapped[str] = mapped_column(String(255), unique=True)
    extracto: Mapped[str] = mapped_column(Text)
    contenido: Mapped[str] = mapped_column(TextoLargo)
    imagen_portada: Mapped[str | None] = mapped_column(String(255))
    fecha_publicacion: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())
    activo: Mapped[bool] = mapped_column(Boolean, default=True)


class ContactSubmodulo(Base):
    """Orden/visibilidad de los sub-módulos internos de 'contact' (mensajes / mapa / datos)."""
    __tablename__ = 'contenido_contact_submodulos'
    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    nombre_legible: Mapped[str] = mapped_column(String(150))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    orden: Mapped[int] = mapped_column(Integer)


class ContactDatos(Base):
    __tablename__ = 'contenido_contact_datos'
    __table_args__ = _singleton('contenido_contact_datos')
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    titulo: Mapped[str] = mapped_column(Text, default='Hablemos')
    subtitulo: Mapped[str | None] = mapped_column(Text)
    telefono: Mapped[str | None] = mapped_column(Text)
    email: Mapped[str | None] = mapped_column(Text)
    ubicacion_texto: Mapped[str | None] = mapped_column(Text)
    horario: Mapped[str | None] = mapped_column(Text)


class ContactMapa(Base):
    """Dirección usada por el mapa embebido de Google Maps."""
    __tablename__ = 'contenido_contact_mapa'
    __table_args__ = _singleton('contenido_contact_mapa')
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    direccion: Mapped[str] = mapped_column(Text)


# ==========================================================
# SEO (landing y blog: mismo shape a propósito)
# ==========================================================
class ConfiguracionSeo(Base):
    __tablename__ = 'configuracion_seo'
    __table_args__ = _singleton('configuracion_seo')
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    meta_titulo: Mapped[str] = mapped_column(Text)
    meta_descripcion: Mapped[str] = mapped_column(Text)
    og_image: Mapped[str | None] = mapped_column(String(255))


class ConfiguracionSeoBlog(Base):
    __tablename__ = 'configuracion_seo_blog'
    __table_args__ = _singleton('configuracion_seo_blog')
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    meta_titulo: Mapped[str] = mapped_column(Text)
    meta_descripcion: Mapped[str] = mapped_column(Text)
    og_image: Mapped[str | None] = mapped_column(String(255))


# ==========================================================
# REDES SOCIALES (una fila por plataforma)
# ==========================================================
class ConfiguracionRedes(Base):
    __tablename__ = 'configuracion_redes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plataforma: Mapped[str] = mapped_column(String(50), unique=True)
    access_token: Mapped[str | None] = mapped_column(Text)
    account_id: Mapped[str | None] = mapped_column(String(100))
    activo_api: Mapped[bool] = mapped_column(Boolean, default=False)


# ==========================================================
# ANALÍTICAS Y MENSAJES
# ==========================================================
class AnaliticaVisita(Base):
    __tablename__ = 'analiticas_visitas'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    ruta: Mapped[str] = mapped_column(String(500))


class MensajeContacto(Base):
    __tablename__ = 'mensajes_contacto'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(String(255))
    mensaje: Mapped[str] = mapped_column(Text)
    fecha_envio: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    leido: Mapped[bool] = mapped_column(Boolean, default=False)
