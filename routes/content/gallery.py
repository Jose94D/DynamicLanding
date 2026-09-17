from flask import render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required

from extensions import get_db_connection
from utils_imagenes import MAX_ANCHO_GALLERY
from . import content_bp
from . helpers import procesar_imagen_subida, eliminar_archivo_si_existe


# ==========================================
# GALERÍA
# ==========================================
@content_bp.route('/gallery', methods=['GET', 'POST'])
@login_required
def editar_gallery():
    conn = get_db_connection()

    if request.method == 'POST':
        if 'imagen' not in request.files or request.files['imagen'].filename == '':
            flash("No se seleccionó ningún archivo", "danger")
            return redirect(request.url)

        file = request.files['imagen']
        titulo = request.form.get('titulo', '')

        try:
            filename = procesar_imagen_subida(
                file,
                carpeta_destino=current_app.config['UPLOAD_FOLDER_GALLERY'],
                max_ancho=MAX_ANCHO_GALLERY
            )
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(request.url)

        # El orden ya no lo escribe el usuario: la imagen nueva simplemente
        # se agrega al final de la galería. El orden final se ajusta luego
        # arrastrando y soltando las imágenes.
        siguiente_orden = conn.execute(
            'SELECT COALESCE(MAX(orden), 0) + 1 AS siguiente FROM contenido_gallery'
        ).fetchone()['siguiente']

        conn.execute(
            'INSERT INTO contenido_gallery (nombre_archivo, titulo, orden) VALUES (?, ?, ?)',
            (filename, titulo, siguiente_orden)
        )
        conn.commit()
        flash("Imagen agregada a la galería.", "success")
        return redirect(url_for('content.editar_gallery'))

    items = conn.execute('SELECT * FROM contenido_gallery ORDER BY orden ASC').fetchall()
    conn.close()
    return render_template('admin/modulos/editar_gallery.html', items=items)


@content_bp.route('/gallery/editar/<int:id>', methods=['POST'])
@login_required
def editar_gallery_item(id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM contenido_gallery WHERE id = ?', (id,)).fetchone()

    if not item:
        conn.close()
        flash("La imagen no existe.", "danger")
        return redirect(url_for('content.editar_gallery'))

    titulo = request.form.get('titulo', '')
    filename = item['nombre_archivo']

    # Reemplazar la imagen es opcional: si no se sube un archivo nuevo,
    # se conserva la imagen actual y solo se actualiza el título.
    file = request.files.get('imagen')
    if file and file.filename != '':
        try:
            nuevo_filename = procesar_imagen_subida(
                file,
                carpeta_destino=current_app.config['UPLOAD_FOLDER_GALLERY'],
                max_ancho=MAX_ANCHO_GALLERY
            )
        except ValueError as e:
            conn.close()
            flash(str(e), "danger")
            return redirect(url_for('content.editar_gallery'))

        eliminar_archivo_si_existe(current_app.config['UPLOAD_FOLDER_GALLERY'], filename)
        filename = nuevo_filename

    conn.execute(
        'UPDATE contenido_gallery SET titulo = ?, nombre_archivo = ? WHERE id = ?',
        (titulo, filename, id)
    )
    conn.commit()
    conn.close()
    flash("Imagen actualizada.", "success")
    return redirect(url_for('content.editar_gallery'))


@content_bp.route('/gallery/eliminar/<int:id>')
@login_required
def eliminar_gallery(id):
    conn = get_db_connection()
    item = conn.execute('SELECT nombre_archivo FROM contenido_gallery WHERE id = ?', (id,)).fetchone()

    if item:
        eliminar_archivo_si_existe(current_app.config['UPLOAD_FOLDER_GALLERY'], item['nombre_archivo'])
        conn.execute('DELETE FROM contenido_gallery WHERE id = ?', (id,))
        conn.commit()
        flash("Imagen eliminada de la galería.", "success")

    conn.close()
    return redirect(url_for('content.editar_gallery'))


@content_bp.route('/gallery/reordenar', methods=['POST'])
@login_required
def reordenar_gallery():
    data = request.get_json(silent=True) or {}
    ids = data.get('orden', [])

    if not isinstance(ids, list) or not ids:
        return jsonify(ok=False), 400

    conn = get_db_connection()
    try:
        for posicion, id_ in enumerate(ids, start=1):
            conn.execute('UPDATE contenido_gallery SET orden = ? WHERE id = ?', (posicion, id_))
        conn.commit()
    except Exception:
        conn.rollback()
        return jsonify(ok=False), 500
    finally:
        conn.close()

    return jsonify(ok=True)