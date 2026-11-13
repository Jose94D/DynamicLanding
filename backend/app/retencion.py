"""
Borra los datos personales que superan el plazo prometido en la política de privacidad.

- Analíticas con consentimiento (visitas y sus eventos): 13 meses. Después solo queda el conteo anónimo de
  páginas vistas (`analiticas_visitas`), que no identifica a nadie.
- Mensajes del formulario de contacto: 24 meses.
El registro de consentimientos se conserva: es la prueba de que se pidió, y no contiene datos personales.

Uso (desde backend/), por ejemplo una vez al día con un cron de cPanel:
    .venv/bin/python -m app.retencion
"""
from datetime import datetime, timedelta

from sqlalchemy import delete

from . import models as m
from .db import SessionLocal

DIAS_ANALITICAS = 395   # 13 meses: permite comparar con el mismo mes del año anterior
DIAS_MENSAJES = 730     # 24 meses


def aplicar(db, ahora: datetime | None = None) -> dict:
    ahora = ahora or datetime.now()
    visitas = db.execute(delete(m.AnaliticaSesion)  # sus eventos se borran solos (ON DELETE CASCADE)
                         .where(m.AnaliticaSesion.inicio < ahora - timedelta(days=DIAS_ANALITICAS))).rowcount
    mensajes = db.execute(delete(m.MensajeContacto)
                          .where(m.MensajeContacto.fecha_envio < ahora - timedelta(days=DIAS_MENSAJES))).rowcount
    db.commit()
    return {'visitas': visitas, 'mensajes': mensajes}


if __name__ == '__main__':
    with SessionLocal() as sesion:
        borrado = aplicar(sesion)
    print(f'Retención aplicada: {borrado["visitas"]} visitas y {borrado["mensajes"]} mensajes borrados.')
