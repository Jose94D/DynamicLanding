from flask import render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required

from extensions import get_db_connection
from utils_imagenes import MAX_ANCHO_TESTIMONIAL
from . import content_bp
from . helpers import procesar_imagen_subida, eliminar_archivo_si_existe


# ==========================================
# TESTIMONIOS
# ==========================================
@content_bp.route('/testimonials', methods=['GET', 'POST'])
@login_required
def editar_testimonials():
    conn = get_db_connection()

    if request.method == 'POST':
        nombre = request.form['nombre']
        cargo = request.form.get('cargo', '')
        texto = request.form['texto']
        calificacion = request.form.get('calificacion', 5, type=int)

        # El orden ya no se ingresa manualmente: el nuevo testimonio se
        # agrega al final de la lista (orden = último orden + 1).
        ultimo_orden = conn.execute(
            'SELECT COALESCE(MAX(orden), 0) AS max_orden FROM contenido_testimonials'
        ).fetchone()['max_orden']
        orden = ultimo_orden + 1

        foto_filename = None
        file = request.files.get('foto')
        if file and file.filename != '':
            try:
                foto_filename = procesar_imagen_subida(
                    file,
                    carpeta_destino=current_app.config['UPLOAD_FOLDER_TESTIMONIALS'],
                    max_ancho=MAX_ANCHO_TESTIMONIAL
                )
            except ValueError as e:
                flash(str(e), "danger")
                return redirect(request.url)

        conn.execute('''
            INSERT INTO contenido_testimonials (nombre, cargo, texto, foto, calificacion, orden)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, cargo, texto, foto_filename, calificacion, orden))
        conn.commit()
        flash("Testimonio agregado exitosamente.", "success")
        return redirect(url_for('content.editar_testimonials'))

    testimonios = conn.execute('SELECT * FROM contenido_testimonials ORDER BY orden ASC').fetchall()
    conn.close()
    return render_template('admin/modulos/editar_testimonials.html', testimonios=testimonios)


@content_bp.route('/testimonials/eliminar/<int:id>')
@login_required
def eliminar_testimonial(id):
    conn = get_db_connection()
    item = conn.execute('SELECT foto FROM contenido_testimonials WHERE id = ?', (id,)).fetchone()

    if item and item['foto']:
        eliminar_archivo_si_existe(current_app.config['UPLOAD_FOLDER_TESTIMONIALS'], item['foto'])

    conn.execute('DELETE FROM contenido_testimonials WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash("Testimonio eliminado.", "success")
    return redirect(url_for('content.editar_testimonials'))


@content_bp.route('/testimonials/reordenar', methods=['POST'])
@login_required
def reordenar_testimonials():
    data = request.get_json(silent=True) or {}
    ids = data.get('orden', [])

    if not ids:
        return jsonify({'ok': False}), 400

    conn = get_db_connection()
    for posicion, item_id in enumerate(ids, start=1):
        conn.execute(
            'UPDATE contenido_testimonials SET orden = ? WHERE id = ?',
            (posicion, item_id)
        )
    conn.commit()
    conn.close()

    return jsonify({'ok': True})