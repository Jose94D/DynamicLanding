from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import get_db_connection
from . import content_bp


# ==========================================
# SOBRE NOSOTROS
# ==========================================
@content_bp.route('/about', methods=['GET', 'POST'])
@login_required
def editar_about():
    conn = get_db_connection()
    if request.method == 'POST':
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        mision = request.form['mision']

        conn.execute('''
            UPDATE contenido_about
            SET titulo = ?, descripcion = ?, mision = ?
            WHERE id = 1
        ''', (titulo, descripcion, mision))
        conn.commit()
        flash("Sección Sobre Nosotros actualizada.", "success")
        return redirect(url_for('content.editar_about'))

    nosotros = conn.execute('SELECT * FROM contenido_about WHERE id = 1').fetchone()
    conn.close()
    return render_template('admin/modulos/editar_about.html', nosotros=nosotros)