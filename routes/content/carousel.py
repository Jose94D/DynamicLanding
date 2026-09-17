from flask import render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required

from extensions import get_db_connection
from utils_imagenes import MAX_ANCHO_CAROUSEL
from . import content_bp
from . helpers import procesar_imagen_subida, eliminar_archivo_si_existe


# ==========================================
# CARRUSEL
# ==========================================
@content_bp.route('/carousel', methods=['GET', 'POST'])
@login_required
def editar_carousel():
    conn = get_db_connection()

    if request.method == 'POST':
        if 'imagen' not in request.files:
            flash("No se seleccionó ningún archivo", "danger")
            return redirect(request.url)

        file = request.files['imagen']
        if file.filename == '':
            flash("El archivo no tiene nombre", "danger")
            return redirect(request.url)

        try:
            filename = procesar_imagen_subida(
                file,
                carpeta_destino=current_app.config['UPLOAD_FOLDER_CAROUSEL'],
                max_ancho=MAX_ANCHO_CAROUSEL
            )
        except ValueError as e:
            flash(str(e), "danger")
            return redirect(request.url)

        conn.execute('INSERT INTO contenido_carousel (nombre_archivo) VALUES (?)', (filename,))
        conn.commit()
        flash("Imagen subida con éxito", "success")
        return redirect(url_for('content.editar_carousel'))

    imagenes = conn.execute('SELECT * FROM contenido_carousel ORDER BY orden ASC').fetchall()
    conn.close()
    return render_template('admin/modulos/editar_carousel.html', imagenes=imagenes)


@content_bp.route('/carousel/eliminar/<int:id>')
@login_required
def eliminar_carousel(id):
    conn = get_db_connection()
    img = conn.execute('SELECT nombre_archivo FROM contenido_carousel WHERE id = ?', (id,)).fetchone()

    if img:
        eliminar_archivo_si_existe(current_app.config['UPLOAD_FOLDER_CAROUSEL'], img['nombre_archivo'])
        conn.execute('DELETE FROM contenido_carousel WHERE id = ?', (id,))
        conn.commit()
        flash("Imagen eliminada.", "success")

    conn.close()
    return redirect(url_for('content.editar_carousel'))


@content_bp.route('/carousel/reordenar', methods=['POST'])
@login_required
def reordenar_carousel():
    data = request.get_json(silent=True) or {}
    ids = data.get('orden', [])

    if not isinstance(ids, list) or not ids:
        return jsonify(ok=False), 400

    conn = get_db_connection()
    try:
        for posicion, id_ in enumerate(ids, start=1):
            conn.execute('UPDATE contenido_carousel SET orden = ? WHERE id = ?', (posicion, id_))
        conn.commit()
    except Exception:
        conn.rollback()
        return jsonify(ok=False), 500
    finally:
        conn.close()

    return jsonify(ok=True)