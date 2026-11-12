import { api, leerForm, useAccion } from '../api'
import { alEnviar, AreaTexto, BotonGuardar, Campo, ConDatos, Pagina } from '../componentes/ui'
import type { Hero as HeroT } from '../tipos'

const RUTA = '/api/admin/hero'

export function Hero() {
  const guardar = useAccion((datos: Record<string, string>) => api(RUTA, { method: 'PUT', json: datos }), [RUTA], 'Hero actualizado.')

  return (
    <Pagina titulo="Hero / Banner" icono="bi-image" descripcion="El banner principal, lo primero que ve un visitante.">
      <ConDatos<HeroT> ruta={RUTA}>
        {(h) => (
          <form className="tarjeta space-y-4" onSubmit={alEnviar((f) => guardar.mutate(leerForm(f)))}>
            <Campo label="Título" name="titulo" defaultValue={h.titulo} required />
            <AreaTexto label="Subtítulo" name="subtitulo" defaultValue={h.subtitulo ?? ''} rows={2} />
            <div className="grid gap-4 sm:grid-cols-2">
              <Campo label="Texto del botón" name="texto_boton" defaultValue={h.texto_boton ?? ''} />
              <Campo label="Enlace del botón" name="url_boton" defaultValue={h.url_boton ?? ''} ayuda="Ej: #contact o https://…" />
            </div>
            <BotonGuardar pendiente={guardar.isPending} />
          </form>
        )}
      </ConDatos>
    </Pagina>
  )
}
