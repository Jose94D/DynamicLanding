import { useState } from 'react'
import { api, leerForm, useAccion } from '../api'
import { alEnviar, BotonGuardar, Campo, ConDatos, Pagina } from '../componentes/ui'
import type { Seo as SeoT } from '../tipos'

const MAX_TITULO = 60
const MAX_DESCRIPCION = 160

/** Sirve para el SEO del sitio y el del blog: misma forma y mismas reglas. */
export function Seo({ ruta, titulo }: { ruta: string; titulo: string }) {
  return (
    <Pagina titulo={titulo} icono="bi-search" descripcion="Cómo aparece la página en Google y al compartirla en redes.">
      <ConDatos<SeoT> ruta={ruta}>{(seo) => <Formulario ruta={ruta} seo={seo} />}</ConDatos>
    </Pagina>
  )
}

function Formulario({ ruta, seo }: { ruta: string; seo: SeoT }) {
  const [largos, setLargos] = useState({ meta_titulo: seo.meta_titulo.length, meta_descripcion: seo.meta_descripcion.length })
  const guardar = useAccion((datos: Record<string, string>) => api(ruta, { method: 'PUT', json: datos }), [ruta], 'Configuración SEO guardada.')

  return (
    <form
      className="tarjeta space-y-4"
      onSubmit={alEnviar((f) => guardar.mutate(leerForm(f)))}
      onInput={(e) => {
        const { name, value } = e.target as HTMLInputElement
        if (name in largos) setLargos({ ...largos, [name]: value.length })
      }}
    >
      <Campo label="Título" name="meta_titulo" defaultValue={seo.meta_titulo} maxLength={MAX_TITULO} required
        ayuda={`${largos.meta_titulo}/${MAX_TITULO} caracteres`} />
      <Campo label="Descripción" name="meta_descripcion" defaultValue={seo.meta_descripcion} maxLength={MAX_DESCRIPCION} required
        ayuda={`${largos.meta_descripcion}/${MAX_DESCRIPCION} caracteres`} />
      <Campo label="Imagen para redes (og:image)" name="og_image" defaultValue={seo.og_image ?? ''}
        ayuda="Nombre del archivo dentro de static/img, ej: portada.jpg" />
      <BotonGuardar pendiente={guardar.isPending} />
    </form>
  )
}
