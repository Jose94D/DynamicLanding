import { useRef, useState } from 'react'
import { ICONOS } from '../iconos'

/** Botón que abre un diálogo con la grilla de íconos. Guarda el valor en un input oculto `name`. */
export function SelectorIcono({ name, inicial = 'bi-star' }: { name: string; inicial?: string }) {
  const [icono, setIcono] = useState(inicial)
  const [filtro, setFiltro] = useState('')
  const dialogo = useRef<HTMLDialogElement>(null)
  const visibles = ICONOS.filter((i) => i.includes(filtro.trim().toLowerCase()))

  function elegir(i: string) {
    setIcono(i)
    dialogo.current?.close()
  }

  return (
    <div>
      <span className="etiqueta">Ícono</span>
      <input type="hidden" name={name} value={icono} />
      <button type="button" className="boton-sec" aria-label={`Ícono ${icono.replace('bi-', '')}, cambiar`} onClick={() => dialogo.current?.showModal()}>
        <i className={`bi ${icono} text-lg`} aria-hidden /> {icono.replace('bi-', '')} <span className="text-zinc-400">· cambiar</span>
      </button>

      <dialog ref={dialogo} className="m-auto w-[min(36rem,calc(100vw-2rem))] rounded-xl p-0 shadow-xl backdrop:bg-black/40">
        <div className="flex items-center gap-3 border-b border-zinc-200 p-4">
          <input
            className="campo"
            placeholder="Buscar ícono (ej: casa, house, star)"
            aria-label="Buscar ícono"
            value={filtro}
            onChange={(e) => setFiltro(e.target.value)}
          />
          <button type="button" className="boton-sec" onClick={() => dialogo.current?.close()} aria-label="Cerrar">
            <i className="bi bi-x-lg" aria-hidden />
          </button>
        </div>
        <div className="grid max-h-80 grid-cols-6 gap-1 overflow-y-auto p-4 sm:grid-cols-8">
          {visibles.map((i) => (
            <button
              key={i}
              type="button"
              title={i}
              aria-label={i}
              aria-pressed={i === icono}
              onClick={() => elegir(i)}
              className={`rounded-lg p-2 text-xl hover:bg-zinc-100 focus-visible:ring-2 focus-visible:ring-zinc-500 focus-visible:outline-none ${i === icono ? 'bg-zinc-900 text-white hover:bg-zinc-800' : 'text-zinc-700'}`}
            >
              <i className={`bi ${i}`} aria-hidden />
            </button>
          ))}
          {!visibles.length && <p className="col-span-full text-sm text-zinc-500">Sin resultados.</p>}
        </div>
      </dialog>
    </div>
  )
}
