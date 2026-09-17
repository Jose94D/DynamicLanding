from flask import render_template, request, redirect, url_for, flash, current_app
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
        orden = request.form.get('orden', 1, type=int)

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