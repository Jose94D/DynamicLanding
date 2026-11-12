import { api, imagen, useAccion, useReordenar } from '../api'
import { ListaOrdenable } from '../componentes/ListaOrdenable'
import { alEnviar, AreaTexto, Campo, ConDatos, Pagina, Pista, Vacio } from '../componentes/ui'
import type { Testimonio } from '../tipos'

const RUTA = '/api/admin/testimonios'

const Estrellas = ({ n }: { n: number }) => (
  <span className="text-amber-500" aria-label={`${n} de 5 estrellas`}>
    {Array.from({ length: 5 }, (_, i) => <i key={i} className={`bi ${i < n ? 'bi-star-fill' : 'bi-star'}`} aria-hidden />)}
  </span>
)

export function Testimonios() {
  const crear = useAccion((form: FormData) => api(RUTA, { method: 'POST', form }), [RUTA], 'Testimonio agregado.')
  const eliminar = useAccion((id: number) => api(`${RUTA}/${id}`, { method: 'DELETE' }), [RUTA], 'Testimonio eliminado.')
  const reordenar = useReordenar<Testimonio>(RUTA, `${RUTA}/orden`)

  return (
    <Pagina titulo="Testimonios" icono="bi-chat-quote" descripcion="Opiniones de clientes con foto y calificación.">
      <form className="tarjeta grid gap-4 sm:grid-cols-2" onSubmit={alEnviar((f) => crear.mutate(new FormData(f), { onSuccess: () => f.reset() }))}>
        <h2 className="font-medium text-zinc-900 sm:col-span-2">Nuevo testimonio</h2>
        <Campo label="Nombre" name="nombre" required />
        <Campo label="Cargo o empresa (opcional)" name="cargo" />
        <div className="sm:col-span-2"><AreaTexto label="Testimonio" name="texto" rows={3} required /></div>
        <div>
          <label htmlFor="calificacion" className="etiqueta">Calificación</label>
          <select id="calificacion" name="calificacion" defaultValue="5" className="campo">
            {[5, 4, 3, 2, 1].map((n) => <option key={n} value={n}>{'★'.repeat(n)} ({n})</option>)}
          </select>
        </div>
        <Campo label="Foto (opcional)" name="foto" type="file" accept="image/jpeg,image/png,image/webp" />
        <div className="sm:col-span-2">
          <button className="boton" disabled={crear.isPending}><i className="bi bi-plus-lg" aria-hidden /> Agregar testimonio</button>
        </div>
      </form>

      <ConDatos<Testimonio[]> ruta={RUTA}>
        {(items) => items.length ? (
          <>
            <ListaOrdenable items={items} onOrdenar={reordenar}>
              {(t, asa) => (
                <div className="flex items-center gap-3 rounded-lg border border-zinc-200 bg-white px-3 py-2">
                  {asa}
                  {t.foto
                    ? <img src={imagen('testimonials', t.foto)} alt="" className="h-10 w-10 rounded-full object-cover" />
                    : <span className="flex h-10 w-10 items-center justify-center rounded-full bg-zinc-100 text-zinc-400"><i className="bi bi-person" aria-hidden /></span>}
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-zinc-900">{t.nombre} {t.cargo && <span className="font-normal text-zinc-500">· {t.cargo}</span>}</p>
                    <p className="truncate text-xs text-zinc-500">{t.texto}</p>
                  </div>
                  <Estrellas n={t.calificacion} />
                  <button className="boton-peligro" onClick={() => confirm(`¿Eliminar el testimonio de ${t.nombre}?`) && eliminar.mutate(t.id)}>
                    <i className="bi bi-trash" aria-hidden /><span className="sr-only">Eliminar</span>
                  </button>
                </div>
              )}
            </ListaOrdenable>
            <Pista>Arrastra para cambiar el orden; se guarda automáticamente.</Pista>
          </>
        ) : <Vacio>Aún no hay testimonios.</Vacio>}
      </ConDatos>
    </Pagina>
  )
}
