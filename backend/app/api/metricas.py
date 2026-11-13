"""Métricas del panel de Analíticas para un período (últimos 7, 30, 90 o 365 días), comparadas con el
período anterior de igual largo (ej. últimos 30 días vs. los 30 días previos)."""
from datetime import date, datetime, timedelta

from fastapi import Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .. import models as m
from ..db import get_db
from ..schemas import AnaliticasOut, Consentidas, Conteo, Numeros, NumerosConsentidas, Serie
from .comun import router_admin

router = router_admin('analíticas')

S, V, E, M = m.AnaliticaSesion, m.AnaliticaVisita, m.AnaliticaEvento, m.MensajeContacto
PERIODOS = (7, 30, 90, 365)


def _contar(db, modelo, columna, desde, hasta, *filtros):
    return db.scalar(select(func.count()).select_from(modelo).where(columna >= desde, columna < hasta, *filtros))


def _visitas_con(db, tipo, desde, hasta):
    """Visitas del período con al menos un evento de ese tipo (una visita cuenta una vez aunque lo repita)."""
    return db.scalar(select(func.count(func.distinct(E.session_id))).join(S, S.session_id == E.session_id)
                     .where(E.tipo == tipo, S.inicio >= desde, S.inicio < hasta))


def _numeros(db, desde: datetime, hasta: datetime) -> Numeros:
    """Todas las cifras de un período [desde, hasta)."""
    # Nuevo = su primera visita (de toda la historia) cae dentro del período; recurrente = ya había venido antes.
    primera = select(S.visitor_id, func.min(S.inicio).label('primera')).group_by(S.visitor_id).subquery()
    del_periodo = select(S.visitor_id).where(S.inicio >= desde, S.inicio < hasta).distinct().subquery()
    unicos, nuevos = db.execute(select(func.count(), func.coalesce(func.sum(primera.c.primera >= desde), 0))
                                .select_from(del_periodo).join(primera, primera.c.visitor_id == del_periodo.c.visitor_id)).one()

    visitas = _contar(db, S, S.inicio, desde, hasta)
    con_envio = _visitas_con(db, 'form_submit', desde, hasta)
    galeria = dict(db.execute(select(E.tipo, func.count()).join(S, S.session_id == E.session_id)
                              .where(E.tipo.in_(('gallery_open', 'gallery_navigate')), S.inicio >= desde, S.inicio < hasta)
                              .group_by(E.tipo)).all())
    duracion = db.scalar(select(func.avg(S.segundos_activos)).where(S.inicio >= desde, S.inicio < hasta))

    return Numeros(
        paginas_vistas=_contar(db, V, V.fecha, desde, hasta),
        mensajes_recibidos=_contar(db, M, M.fecha_envio, desde, hasta),
        consentidas=NumerosConsentidas(
            visitas=visitas, visitantes_unicos=unicos, nuevos=int(nuevos), recurrentes=unicos - int(nuevos),
            paginas_vistas=_contar(db, E, E.fecha, desde, hasta, E.tipo == 'pageview'),
            visitas_con_envio=con_envio,
            tasa_conversion=round(con_envio / visitas * 100, 1) if visitas else 0,
            duracion_media=round(duracion or 0),
            aperturas_galeria=galeria.get('gallery_open', 0),
            navegaciones_galeria=galeria.get('gallery_navigate', 0),
            visitas_con_galeria=_visitas_con(db, 'gallery_open', desde, hasta),
        ),
    )


def _desglose(db, columna, desde, hasta):
    """Visitas agrupadas por una columna de la sesión, de mayor a menor. Sin dato (anteriores a la etapa 4) = 'Desconocido'."""
    filas = db.execute(select(columna, func.count()).where(S.inicio >= desde, S.inicio < hasta)
                       .group_by(columna).order_by(func.count().desc()))
    return [Conteo(nombre=n or 'Desconocido', total=t) for n, t in filas]


def _serie(db, desde: datetime, hoy: date, dias: int):
    """Páginas vistas por día (sin huecos: los días sin visitas valen 0). Para 365 días, por mes."""
    if dias == 365:
        mes = func.date_format(V.fecha, '%Y-%m')
        filas = dict(db.execute(select(mes, func.count()).where(V.fecha >= desde).group_by(mes)).all())
        meses = sorted({(desde.date() + timedelta(days=d)).strftime('%Y-%m') for d in range(dias)})
        return [Serie(periodo=p, total=filas.get(p, 0)) for p in meses]
    dia = func.date(V.fecha)
    filas = {str(d): t for d, t in db.execute(select(dia, func.count()).where(V.fecha >= desde).group_by(dia))}
    return [Serie(periodo=str(hoy - timedelta(days=d)), total=filas.get(str(hoy - timedelta(days=d)), 0))
            for d in reversed(range(dias))]


@router.get('/analiticas', response_model=AnaliticasOut)
def analiticas(dias: int = Query(30, description=f'Uno de {PERIODOS}'), db: Session = Depends(get_db)):
    if dias not in PERIODOS:  # un Literal de enteros no acepta el texto que llega en la URL
        raise HTTPException(422, f'El período debe ser uno de {PERIODOS} días.')
    hoy = date.today()
    desde = datetime.combine(hoy - timedelta(days=dias - 1), datetime.min.time())  # incluye hoy completo
    hasta = desde + timedelta(days=dias)
    anterior_desde = desde - timedelta(days=dias)

    actual = _numeros(db, desde, hasta)
    return AnaliticasOut(
        dias=dias, desde=desde.date(), hasta=hoy,
        paginas_vistas=actual.paginas_vistas, mensajes_recibidos=actual.mensajes_recibidos,
        serie=_serie(db, desde, hoy, dias),
        consentidas=Consentidas(
            **actual.consentidas.model_dump(),
            por_origen=_desglose(db, S.origen, desde, hasta),
            por_dispositivo=_desglose(db, S.dispositivo, desde, hasta),
            por_navegador=_desglose(db, S.navegador, desde, hasta),
        ),
        anterior=_numeros(db, anterior_desde, desde),
    )
