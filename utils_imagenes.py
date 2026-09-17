"""
Utilidad de optimización de imágenes para el CMS.

Requiere Pillow:  pip install Pillow

Uso típico dentro de una ruta de subida (carousel, gallery, testimonials):

    from utils.image_utils import guardar_imagen_optimizada

    archivo = request.files['imagen']
    nombre_archivo = guardar_imagen_optimizada(
        archivo,
        carpeta_destino=os.path.join(app.static_folder, 'uploads', 'carousel'),
        max_ancho=1920
    )
    # nombre_archivo es el nombre final (ej: '3f9a1c2b.jpg') para guardar en la BD,
    # igual que antes hacías con secure_filename(archivo.filename).
"""

import os
import uuid
from PIL import Image, ImageOps

# Extensiones que aceptamos procesar como imagen
EXTENSIONES_VALIDAS = {'.jpg', '.jpeg', '.png', '.webp'}

# Presets sugeridos por módulo (ajusta a gusto)
MAX_ANCHO_CAROUSEL = 1920
MAX_ANCHO_GALLERY = 1200
MAX_ANCHO_TESTIMONIAL = 500  # son fotos de perfil, no necesitan ser grandes

CALIDAD_JPEG = 82  # 80-85 es el punto dulce entre peso y calidad visual


def guardar_imagen_optimizada(file_storage, carpeta_destino, max_ancho=1600, calidad=CALIDAD_JPEG):
    """
    Recibe un objeto FileStorage (de request.files), lo optimiza y lo guarda en disco.

    - Corrige la rotación según metadata EXIF (fotos de celular).
    - Redimensiona si el ancho excede max_ancho, manteniendo la proporción.
    - Elimina metadata EXIF/GPS (privacidad + menos peso).
    - Re-comprime siempre como JPEG (excepto si el original es PNG con transparencia,
      en cuyo caso se conserva como PNG).

    Retorna: el nombre de archivo final (str) que debes guardar en la base de datos.
    Lanza ValueError si el archivo no es una imagen válida.
    """
    extension_original = os.path.splitext(file_storage.filename)[1].lower()
    if extension_original not in EXTENSIONES_VALIDAS:
        raise ValueError(f"Formato no soportado: {extension_original}")

    try:
        imagen = Image.open(file_storage.stream)
        imagen.verify()  # valida que sea un archivo de imagen real, no algo disfrazado
        file_storage.stream.seek(0)
        imagen = Image.open(file_storage.stream)
    except Exception:
        raise ValueError("El archivo subido no es una imagen válida o está corrupto.")

    # 1. Corregir orientación según EXIF (evita fotos "acostadas")
    imagen = ImageOps.exif_transpose(imagen)

    # 2. Redimensionar si excede el ancho máximo
    if imagen.width > max_ancho:
        proporcion = max_ancho / float(imagen.width)
        nuevo_alto = int(imagen.height * proporcion)
        imagen = imagen.resize((max_ancho, nuevo_alto), Image.LANCZOS)

    # 3. Decidir formato de salida
    tiene_transparencia = imagen.mode in ('RGBA', 'LA') or (
        imagen.mode == 'P' and 'transparency' in imagen.info
    )

    os.makedirs(carpeta_destino, exist_ok=True)
    nombre_base = uuid.uuid4().hex

    if tiene_transparencia:
        # Conservamos PNG para no perder transparencia (logos, iconos con fondo transparente)
        nombre_final = f"{nombre_base}.png"
        ruta_final = os.path.join(carpeta_destino, nombre_final)
        imagen.save(ruta_final, format="PNG", optimize=True)
    else:
        # Todo lo demás (fotos de carrusel, galería, testimonios) se recomprime como JPEG
        imagen = imagen.convert("RGB")  # necesario si venía de PNG/paleta sin transparencia
        nombre_final = f"{nombre_base}.jpg"
        ruta_final = os.path.join(carpeta_destino, nombre_final)
        imagen.save(ruta_final, format="JPEG", quality=calidad, optimize=True)
        # exif=b"" ya queda excluido: Pillow no reescribe EXIF salvo que se lo pases explícitamente

    return nombre_final