"""
Helpers internos del paquete `content`, compartidos entre carousel, gallery
y testimonials (las tres secciones que suben/borran imágenes).

No expone rutas propias, por eso el guion bajo en el nombre del archivo:
así queda claro que es un módulo de soporte y no una sección del CMS.
"""

import os

from utils_imagenes import guardar_imagen_optimizada


def procesar_imagen_subida(file_storage, carpeta_destino, max_ancho):
    """
    Wrapper delgado sobre guardar_imagen_optimizada, pensado para llamarse
    directo desde las rutas de subida. Devuelve el nombre de archivo final
    o lanza ValueError si el archivo no es una imagen válida.
    """
    return guardar_imagen_optimizada(
        file_storage,
        carpeta_destino=carpeta_destino,
        max_ancho=max_ancho,
    )


def eliminar_archivo_si_existe(carpeta, nombre_archivo):
    """Borra un archivo físico del disco si existe. No falla si ya no está."""
    if not nombre_archivo:
        return
    ruta = os.path.join(carpeta, nombre_archivo)
    if os.path.exists(ruta):
        os.remove(ruta)