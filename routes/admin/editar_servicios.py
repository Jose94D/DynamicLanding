from flask import request, redirect, url_for, flash, render_template, jsonify
from flask_login import login_required

from extensions import get_db_connection
from . import content_bp


# ==========================================
# SERVICIOS
# ==========================================
@content_bp.route('/servicios', methods=['GET', 'POST'])
@login_required
def editar_servicios():
    conn = get_db_connection()
    if request.method == 'POST':
        icono = request.form['icono']
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        orden = request.form.get('orden', 1, type=int)

        conn.execute('INSERT INTO contenido_services (icono, titulo, descripcion, orden) VALUES (?, ?, ?, ?)',
                     (icono, titulo, descripcion, orden))
        conn.commit()
        flash("Servicio agregado exitosamente.", "success")
        return redirect(url_for('content.editar_servicios'))

    servicios = conn.execute('SELECT * FROM contenido_services ORDER BY orden ASC').fetchall()
    conn.close()
    return render_template('admin/modulos/editar_servicios.html', servicios=servicios)


@content_bp.route('/servicios/editar/<int:id>', methods=['POST'])
@login_required
def editar_servicio(id):
    conn = get_db_connection()
    servicio = conn.execute('SELECT id FROM contenido_services WHERE id = ?', (id,)).fetchone()

    if not servicio:
        conn.close()
        flash("El servicio que intentas editar no existe.", "danger")
        return redirect(url_for('content.editar_servicios'))

    icono = request.form['icono']
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    orden = request.form.get('orden', 1, type=int)

    conn.execute('''
        UPDATE contenido_services
        SET icono = ?, titulo = ?, descripcion = ?, orden = ?
        WHERE id = ?
    ''', (icono, titulo, descripcion, orden, id))
    conn.commit()
    conn.close()
    flash("Servicio actualizado exitosamente.", "success")
    return redirect(url_for('content.editar_servicios'))


@content_bp.route('/servicios/eliminar/<int:id>')
@login_required
def eliminar_servicio(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM contenido_services WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash("Servicio eliminado.", "success")
    return redirect(url_for('content.editar_servicios'))


@content_bp.route('/servicios/reordenar', methods=['POST'])
@login_required
def reordenar_servicios():
    """Recibe la nueva secuencia de IDs (tras un drag & drop) y reescribe
    el campo 'orden' de cada servicio según su posición en la lista."""
    data = request.get_json(silent=True)
    if not data or 'orden' not in data or not isinstance(data['orden'], list):
        return jsonify({"ok": False, "error": "Datos inválidos"}), 400

    conn = get_db_connection()
    try:
        for posicion, servicio_id in enumerate(data['orden'], start=1):
            conn.execute(
                'UPDATE contenido_services SET orden = ? WHERE id = ?',
                (posicion, int(servicio_id))
            )
        conn.commit()
    except (ValueError, TypeError):
        conn.close()
        return jsonify({"ok": False, "error": "IDs inválidos"}), 400

    conn.close()
    return jsonify({"ok": True})