"""
Optimización de imágenes subidas (recibe UploadFile de FastAPI).
"""
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps

from .config import UPLOADS_DIR

EXTENSIONES_VALIDAS = {'.jpg', '.jpeg', '.png', '.webp'}

MAX_ANCHO_CAROUSEL = 1920
MAX_ANCHO_GALLERY = 1200
MAX_ANCHO_ABOUT = 1600  # ocupa media pantalla; 1600 cubre pantallas retina
MAX_ANCHO_TESTIMONIAL = 500  # fotos de perfil

CALIDAD_JPEG = 82  # 80-85: punto dulce entre peso y calidad visual


def carpeta(nombre: str) -> Path:
    return UPLOADS_DIR / nombre


def guardar_imagen_optimizada(archivo: UploadFile, carpeta_destino: Path, max_ancho=1600, calidad=CALIDAD_JPEG) -> str:
    """
    Corrige la rotación EXIF, redimensiona si excede max_ancho, elimina metadata (EXIF/GPS) y
    recomprime como JPEG (o PNG si tiene transparencia). Devuelve el nombre de archivo final.
    Lanza ValueError si el archivo no es una imagen válida.
    """
    extension = Path(archivo.filename or '').suffix.lower()
    if extension not in EXTENSIONES_VALIDAS:
        raise ValueError(f'Formato no soportado: {extension or "sin extensión"}')

    try:
        imagen = Image.open(archivo.file)
        imagen.verify()  # valida que sea una imagen real, no algo disfrazado
        archivo.file.seek(0)
        imagen = Image.open(archivo.file)
    except Exception:
        raise ValueError('El archivo subido no es una imagen válida o está corrupto.')

    imagen = ImageOps.exif_transpose(imagen)
    if imagen.width > max_ancho:
        imagen = imagen.resize((max_ancho, int(imagen.height * max_ancho / imagen.width)), Image.LANCZOS)

    tiene_transparencia = imagen.mode in ('RGBA', 'LA') or (imagen.mode == 'P' and 'transparency' in imagen.info)
    carpeta_destino.mkdir(parents=True, exist_ok=True)
    nombre_base = uuid.uuid4().hex

    if tiene_transparencia:
        nombre_final = f'{nombre_base}.png'
        imagen.save(carpeta_destino / nombre_final, format='PNG', optimize=True)
    else:
        nombre_final = f'{nombre_base}.jpg'
        imagen.convert('RGB').save(carpeta_destino / nombre_final, format='JPEG', quality=calidad, optimize=True)
    return nombre_final


def subir(archivo: UploadFile, nombre_carpeta: str, max_ancho: int) -> str:
    """guardar_imagen_optimizada con el error convertido en respuesta 400 para la API."""
    try:
        return guardar_imagen_optimizada(archivo, carpeta(nombre_carpeta), max_ancho)
    except ValueError as e:
        raise HTTPException(400, str(e))


def eliminar(nombre_carpeta: str, nombre_archivo: str | None):
    """Borra el archivo del disco si existe. No falla si ya no está."""
    if nombre_archivo:
        (carpeta(nombre_carpeta) / Path(nombre_archivo).name).unlink(missing_ok=True)
