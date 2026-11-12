import { useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, leerForm, useAccion } from '../api'
import { Editor } from '../componentes/Editor'
import { alEnviar, AreaTexto, BotonGuardar, Campo, ConDatos, Interruptor, Pagina, Vacio } from '../componentes/ui'
import type { Articulo, ArticuloResumen } from '../tipos'

const RUTA = '/api/admin/blog'

const fecha =(iso: string | null) =>
  iso ? new Date(iso).toLocaleDateString('es-CL', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'

export function Blog() {
  const eliminar = useAccion((id: number) => api(`${RUTA}/${id}`, { method: 'DELETE' }), [RUTA], 'Artículo eliminado.')

  return (
    <Pagina titulo="Blog" icono="bi-journal-text" descripcion="Artículos publicados y borradores.">
      <Link to="/blog/nuevo" className="boton"><i className="bi bi-plus-lg" aria-hidden /> Nuevo artículo</Link>
      <ConDatos<ArticuloResumen[]> ruta={RUTA}>
        {(articulos) => articulos.length ? (
          <ul className="divide-y divide-zinc-200 overflow-hidden rounded-xl border border-zinc-200 bg-white">
            {articulos.map((a) => (
              <li key={a.id} className="flex flex-wrap items-center gap-3 px-4 py-3">
                <div className="min-w-0 flex-1">
                  <Link to={`/blog/${a.id}`} className="font-medium text-zinc-900 hover:underline">{a.titulo}</Link>
                  <p className="text-xs text-zinc-500">
                    {fecha(a.fecha_publicacion)} ·{' '}
                    <span className={a.activo ? 'text-emerald-700' : 'text-amber-700'}>{a.activo ? 'Publicado' : 'Borrador'}</span>
                  </p>
                </div>
                <a href={`/articulo/${a.id}`} target="_blank" rel="noopener" className="boton-sec">
                  <i className="bi bi-eye" aria-hidden /> Ver
                </a>
                <Link to={`/blog/${a.id}`} className="boton-sec"><i className="bi bi-pencil" aria-hidden /> Editar</Link>
                <button className="boton-peligro" onClick={() => confirm(`¿Eliminar "${a.titulo}"? No se puede deshacer.`) && eliminar.mutate(a.id)}>
                  <i className="bi bi-trash" aria-hidden /><span className="sr-only">Eliminar</span>
                </button>
              </li>
            ))}
          </ul>
        ) : <Vacio>Todavía no hay artículos.</Vacio>}
      </ConDatos>
    </Pagina>
  )
}

/** Crear (/blog/nuevo) o editar (/blog/:id) un artículo. */
export function EditarArticulo() {
  const { id } = useParams()
  const nuevo = id === 'nuevo'
  const vacio: Articulo = { id: 0, titulo: '', slug: '', extracto: '', contenido: '', fecha_publicacion: null, activo: true }

  return (
    <Pagina titulo={nuevo ? 'Nuevo artículo' : 'Editar artículo'} icono="bi-pencil-square">
      <Link to="/blog" className="text-sm text-zinc-600 hover:underline"><i className="bi bi-arrow-left" aria-hidden /> Volver al blog</Link>
      {nuevo ? <Formulario articulo={vacio} /> : <ConDatos<Articulo> ruta={`${RUTA}/${id}`}>{(a) => <Formulario articulo={a} />}</ConDatos>}
    </Pagina>
  )
}

function Formulario({ articulo }: { articulo: Articulo }) {
  const navegar = useNavigate()
  const [contenido, setContenido] = useState(articulo.contenido)
  const [falta, setFalta] = useState(false)
  const nuevo = !articulo.id
  const guardar = useAccion(
    (datos: object) => api<Articulo>(nuevo ? RUTA : `${RUTA}/${articulo.id}`, { method: nuevo ? 'POST' : 'PUT', json: datos }),
    [RUTA, `${RUTA}/${articulo.id}`],
    nuevo ? 'Artículo creado.' : 'Artículo actualizado.',
  )

  return (
    <form
      className="tarjeta space-y-4"
      onSubmit={alEnviar((f) => {
        if (!contenido) return setFalta(true)
        const activo = (f.elements.namedItem('activo') as HTMLInputElement).checked
        guardar.mutate({ ...leerForm(f), contenido, activo }, { onSuccess: () => navegar('/blog') })
      })}
    >
      <Campo label="Título" name="titulo" defaultValue={articulo.titulo} required />
      <AreaTexto label="Extracto" name="extracto" defaultValue={articulo.extracto} rows={2} required />
      <div>
        <span className="etiqueta">Contenido</span>
        <Editor inicial={articulo.contenido} etiqueta="Contenido del artículo" onChange={(html) => { setContenido(html); setFalta(false) }} />
        {falta && <p role="alert" className="mt-1 text-sm text-red-600">El contenido no puede quedar vacío.</p>}
      </div>
      <Interruptor name="activo" label="Publicado (si lo apagas queda como borrador)" checked={articulo.activo} />
      {!nuevo && <p className="text-xs text-zinc-500">Dirección: /articulo/{articulo.id} · el slug ({articulo.slug}) no cambia al editar el título.</p>}
      <BotonGuardar pendiente={guardar.isPending} texto={nuevo ? 'Publicar' : 'Guardar cambios'} />
    </form>
  )
}
