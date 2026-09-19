from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import get_db_connection
from . import content_bp


# ==========================================
# HERO
# ==========================================
@content_bp.route('/hero', methods=['GET', 'POST'])
@login_required
def editar_hero():
    conn = get_db_connection()
    if request.method == 'POST':
        titulo = request.form['titulo']
        subtitulo = request.form['subtitulo']
        texto_boton = request.form['texto_boton']
        url_boton = request.form['url_boton']

        conn.execute('''
            UPDATE contenido_hero
            SET titulo = ?, subtitulo = ?, texto_boton = ?, url_boton = ?
            WHERE id = 1
        ''', (titulo, subtitulo, texto_boton, url_boton))
        conn.commit()
        flash("¡Contenido del Hero actualizado!", "success")
        return redirect(url_for('content.editar_hero'))

    hero_data = conn.execute('SELECT * FROM contenido_hero WHERE id = 1').fetchone()
    conn.close()
    return render_template('admin/modulos/editar_hero.html', hero=hero_data)