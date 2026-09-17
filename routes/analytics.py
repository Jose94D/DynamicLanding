from flask import Blueprint, render_template
from flask_login import login_required
from extensions import get_db_connection

analytics_bp = Blueprint('analytics', __name__, url_prefix='/admin')


@analytics_bp.route('/analiticas')
@login_required
def analiticas():
    conn = get_db_connection()

    total_visitas = conn.execute(
        'SELECT COUNT(*) as total FROM analiticas_visitas'
    ).fetchone()['total']

    # Desglose mensual (para el gráfico de líneas)
    por_mes = conn.execute('''
        SELECT strftime('%Y-%m', fecha) AS periodo, COUNT(*) AS total
        FROM analiticas_visitas
        GROUP BY periodo
        ORDER BY periodo ASC
    ''').fetchall()

    # Desglose anual (para el gráfico y la tarjeta de resumen)
    por_anio = conn.execute('''
        SELECT strftime('%Y', fecha) AS anio, COUNT(*) AS total
        FROM analiticas_visitas
        GROUP BY anio
        ORDER BY anio ASC
    ''').fetchall()

    # Desglose semanal (para el gráfico)
    por_semana = conn.execute('''
        SELECT strftime('%Y-%W', fecha) AS periodo, COUNT(*) AS total
        FROM analiticas_visitas
        GROUP BY periodo
        ORDER BY periodo ASC
    ''').fetchall()

    # Totales del período actual (para las tarjetas de resumen)
    visitas_anio_actual = conn.execute('''
        SELECT COUNT(*) as total FROM analiticas_visitas
        WHERE strftime('%Y', fecha) = strftime('%Y', 'now')
    ''').fetchone()['total']

    visitas_mes_actual = conn.execute('''
        SELECT COUNT(*) as total FROM analiticas_visitas
        WHERE strftime('%Y-%m', fecha) = strftime('%Y-%m', 'now')
    ''').fetchone()['total']

    visitas_semana_actual = conn.execute('''
        SELECT COUNT(*) as total FROM analiticas_visitas
        WHERE strftime('%Y-%W', fecha) = strftime('%Y-%W', 'now')
    ''').fetchone()['total']

    conn.close()

    return render_template(
        'admin/modulos/analiticas.html',
        total_visitas=total_visitas,
        por_mes=por_mes,
        por_anio=por_anio,
        por_semana=por_semana,
        visitas_anio_actual=visitas_anio_actual,
        visitas_mes_actual=visitas_mes_actual,
        visitas_semana_actual=visitas_semana_actual
    )