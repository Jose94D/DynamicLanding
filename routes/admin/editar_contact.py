from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required

from extensions import get_db_connection
from . import content_bp


# ==========================================
# CONTÁCTANOS
# Administra: orden/visibilidad de los 3 sub-módulos internos
# (mensajes / mapa / datos), los datos de contacto y la dirección del mapa.
# ==========================================
@content_bp.route('/contact', methods=['GET', 'POST'])
@login_required
def editar_contact():
    conn = get_db_connection()

    if request.method == 'POST':
        # --- Orden y visibilidad de los sub-módulos ---
        submodulos = conn.execute('SELECT id FROM contenido_contact_submodulos').fetchall()
        for sub in submodulos:
            sub_id = sub['id']
            activo = 1 if request.form.get(f'activo_{sub_id}') else 0
            orden = request.form.get(f'orden_{sub_id}', 1)
            conn.execute('''
                UPDATE contenido_contact_submodulos
                SET activo = ?, orden = ?
                WHERE id = ?
            ''', (activo, orden, sub_id))

        # --- Datos de contacto ---
        titulo = request.form.get('titulo', '').strip()
        subtitulo = request.form.get('subtitulo', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        ubicacion_texto = request.form.get('ubicacion_texto', '').strip()
        horario = request.form.get('horario', '').strip()

        conn.execute('''
            UPDATE contenido_contact_datos
            SET titulo = ?, subtitulo = ?, telefono = ?, email = ?,
                ubicacion_texto = ?, horario = ?
            WHERE id = 1
        ''', (titulo, subtitulo, telefono, email, ubicacion_texto, horario))

        # --- Dirección del mapa ---
        direccion = request.form.get('direccion', '').strip()
        conn.execute('''
            UPDATE contenido_contact_mapa
            SET direccion = ?
            WHERE id = 1
        ''', (direccion,))

        conn.commit()
        conn.close()
        flash("Sección Contáctanos actualizada.", "success")
        return redirect(url_for('content.editar_contact'))

    submodulos = conn.execute('SELECT * FROM contenido_contact_submodulos ORDER BY orden ASC').fetchall()
    datos = conn.execute('SELECT * FROM contenido_contact_datos WHERE id = 1').fetchone()
    mapa = conn.execute('SELECT * FROM contenido_contact_mapa WHERE id = 1').fetchone()
    conn.close()

    return render_template(
        'admin/modulos/editar_contact.html',
        submodulos=submodulos,
        datos=datos,
        mapa=mapa
    )