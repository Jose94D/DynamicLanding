from datetime import datetime
import re

from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import get_db_connection

public_bp = Blueprint('public', __name__)

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

MESES_ES = {
    1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
    5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
    9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
}


def _parsear_fecha(valor):
    """Intenta convertir fecha_publicacion (texto) a datetime, tolerando
    los formatos más comunes en que SQLite suele guardar fechas."""
    if not valor:
        return None
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(valor, fmt)
        except (ValueError, TypeError):
            continue
    return None


def _agrupar_por_mes(articulos):
    """Agrupa una lista de artículos (ya ordenada DESC por fecha) en
    bloques por mes/año, para la barra lateral de archivo. Se usa tanto
    en el listado del blog como en la barra lateral del detalle de un
    artículo, para que ambas vistas muestren siempre lo mismo."""
    grupos = []
    grupos_por_key = {}

    for articulo in articulos:
        fecha = _parsear_fecha(articulo['fecha_publicacion'])
        if fecha:
            key = fecha.strftime('%Y-%m')
            label = f"{MESES_ES[fecha.month]} {fecha.year}"
        else:
            key = 'sin-fecha'
            label = 'Sin fecha'

        if key not in grupos_por_key:
            grupo = {'key': key, 'label': label, 'articulos': []}
            grupos_por_key[key] = grupo
            grupos.append(grupo)

        grupos_por_key[key]['articulos'].append(articulo)

    return grupos


@public_bp.before_request
def registrar_visita():
    """Registra cada visita a una página pública (para el módulo de Analíticas)."""
    conn = get_db_connection()
    conn.execute('INSERT INTO analiticas_visitas (ruta) VALUES (?)', (request.path,))
    conn.commit()
    conn.close()


@public_bp.route('/')
def index():
    conn = get_db_connection()
    seo = conn.execute('SELECT * FROM configuracion_seo WHERE id = 1').fetchone()
    modulos_activos = conn.execute('SELECT id FROM modulos WHERE activo = 1 ORDER BY orden ASC').fetchall()

    hero_data = conn.execute('SELECT * FROM contenido_hero WHERE id = 1').fetchone()
    carousel_data = conn.execute('SELECT * FROM contenido_carousel ORDER BY orden ASC').fetchall()
    services_data = conn.execute('SELECT * FROM contenido_services ORDER BY orden ASC').fetchall()
    gallery_data = conn.execute('SELECT * FROM contenido_gallery ORDER BY orden ASC').fetchall()
    testimonials_data = conn.execute('SELECT * FROM contenido_testimonials ORDER BY orden ASC').fetchall()
    blog_data = conn.execute('''
        SELECT * FROM contenido_blog WHERE activo = 1
        ORDER BY fecha_publicacion DESC LIMIT 3
    ''').fetchall()
    about_data = conn.execute('SELECT * FROM contenido_about WHERE id = 1').fetchone()

    conn.close()
    return render_template(
        'public/index.html',
        seo=seo,
        modulos=modulos_activos,
        hero=hero_data,
        carousel=carousel_data,
        services=services_data,
        gallery=gallery_data,
        testimonials=testimonials_data,
        blog=blog_data,
        about=about_data
    )


@public_bp.route('/articulo/<int:id>')
def ver_articulo(id):
    conn = get_db_connection()
    articulo = conn.execute('SELECT * FROM contenido_blog WHERE id = ?', (id,)).fetchone()

    if not articulo:
        conn.close()
        return "Artículo no encontrado", 404

    # Misma barra lateral de archivo por mes que en el listado del blog,
    # para que el detalle de un artículo se sienta parte del mismo módulo.
    otros_articulos = conn.execute('''
        SELECT * FROM contenido_blog WHERE activo = 1
        ORDER BY fecha_publicacion DESC
    ''').fetchall()
    conn.close()

    grupos = _agrupar_por_mes(otros_articulos)

    # Determina a qué mes pertenece este artículo, para resaltarlo en la sidebar.
    fecha_articulo = _parsear_fecha(articulo['fecha_publicacion'])
    mes_actual = fecha_articulo.strftime('%Y-%m') if fecha_articulo else 'sin-fecha'

    return render_template('public/post.html', articulo=articulo, grupos=grupos, mes_actual=mes_actual)


@public_bp.route('/blog')
def blog_archivo():
    """Listado completo del blog, agrupado por mes/año para la barra
    lateral de archivo (del más reciente al más antiguo)."""
    conn = get_db_connection()
    articulos = conn.execute('''
        SELECT * FROM contenido_blog WHERE activo = 1
        ORDER BY fecha_publicacion DESC
    ''').fetchall()
    conn.close()

    grupos = _agrupar_por_mes(articulos)

    return render_template('public/blog_index.html', grupos=grupos)


@public_bp.route('/contacto', methods=['POST'])
def enviar_contacto():
    nombre = request.form.get('nombre', '').strip()
    email = request.form.get('email', '').strip()
    mensaje = request.form.get('mensaje', '').strip()

    # Honeypot anti-spam: campo oculto que un humano nunca llena
    if request.form.get('sitio_web'):
        return redirect(url_for('public.index') + '#contact')

    if not nombre or not email or not mensaje:
        flash("Por favor completa todos los campos del formulario.", "danger")
        return redirect(url_for('public.index') + '#contact')

    if not EMAIL_REGEX.match(email):
        flash("Por favor ingresa un correo electrónico válido.", "danger")
        return redirect(url_for('public.index') + '#contact')

    conn = get_db_connection()
    conn.execute(
        'INSERT INTO mensajes_contacto (nombre, email, mensaje) VALUES (?, ?, ?)',
        (nombre, email, mensaje)
    )
    conn.commit()
    conn.close()

    flash("¡Gracias! Tu mensaje fue enviado correctamente, te contactaremos pronto.", "success")
    return redirect(url_for('public.index') + '#contact')