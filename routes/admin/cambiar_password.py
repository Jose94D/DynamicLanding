from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import get_db_connection

from . import auth_bp


@auth_bp.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    if request.method == 'POST':
        password_actual = request.form['password_actual']
        password_nueva = request.form['password_nueva']
        password_confirmar = request.form['password_confirmar']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM admin WHERE id = ?', (current_user.id,)).fetchone()

        if not user or not check_password_hash(user['password_hash'], password_actual):
            conn.close()
            flash("La contraseña actual no es correcta.", "danger")
            return redirect(url_for('auth.cambiar_password'))

        if len(password_nueva) < 8:
            conn.close()
            flash("La nueva contraseña debe tener al menos 8 caracteres.", "danger")
            return redirect(url_for('auth.cambiar_password'))

        if password_nueva != password_confirmar:
            conn.close()
            flash("La nueva contraseña y su confirmación no coinciden.", "danger")
            return redirect(url_for('auth.cambiar_password'))

        conn.execute(
            'UPDATE admin SET password_hash = ? WHERE id = ?',
            (generate_password_hash(password_nueva), current_user.id)
        )
        conn.commit()
        conn.close()
        flash("Contraseña actualizada exitosamente.", "success")
        return redirect(url_for('dashboard.dashboard'))

    return render_template('admin/modulos/cambiar_password.html')
