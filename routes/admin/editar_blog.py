import os

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import get_db_connection
from utils import generar_slug
from . import content_bp


# ==========================================
# BLOG
# ==========================================
@content_bp.route('/blog', methods=['GET', 'POST'])
@login_required
def editar_blog():
    conn = get_db_connection()
    if request.method == 'POST':
        titulo = request.form['titulo']
        extracto = request.form['extracto']
        contenido = request.form['contenido']

        slug_base = generar_slug(titulo)
        existe = conn.execute('SELECT id FROM contenido_blog WHERE slug = ?', (slug_base,)).fetchone()
        slug = slug_base if not existe else f"{slug_base}-{os.urandom(2).hex()}"

        conn.execute(
            'INSERT INTO contenido_blog (titulo, slug, extracto, contenido) VALUES (?, ?, ?, ?)',
            (titulo, slug, extracto, contenido)
        )
        conn.commit()
        flash("Artículo publicado exitosamente.", "success")
        return redirect(url_for('content.editar_blog'))

    articulos = conn.execute('SELECT * FROM contenido_blog ORDER BY fecha_publicacion DESC').fetchall()
    conn.close()
    return render_template('admin/modulos/editar_blog.html', articulos=articulos)


@content_bp.route('/blog/eliminar/<int:id>')
@login_required
def eliminar_articulo(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM contenido_blog WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash("Artículo eliminado.", "success")
    return redirect(url_for('content.editar_blog'))


@content_bp.route('/blog/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_articulo(id):
    conn = get_db_connection()
    articulo = conn.execute('SELECT * FROM contenido_blog WHERE id = ?', (id,)).fetchone()

    if not articulo:
        conn.close()
        flash("El artículo que intentas editar no existe.", "danger")
        return redirect(url_for('content.editar_blog'))

    if request.method == 'POST':
        titulo = request.form['titulo']
        extracto = request.form['extracto']
        contenido = request.form['contenido']
        activo = 1 if request.form.get('activo') else 0

        # El slug NO se regenera al editar: así no se rompen links ya compartidos
        # del artículo, aunque el usuario cambie el título.
        conn.execute('''
            UPDATE contenido_blog
            SET titulo = ?, extracto = ?, contenido = ?, activo = ?
            WHERE id = ?
        ''', (titulo, extracto, contenido, activo, id))
        conn.commit()
        conn.close()
        flash("Artículo actualizado exitosamente.", "success")
        return redirect(url_for('content.editar_blog'))

    conn.close()
    return render_template('admin/modulos/editar_articulo.html', articulo=articulo)