import type { FormEvent, InputHTMLAttributes, ReactNode, TextareaHTMLAttributes } from 'react'
import { useDatos } from '../api'

/** Carga una ruta de la API y renderiza `children(datos)` cuando llega (con estados de carga y error). */
export function ConDatos<T>({ ruta, children }: { ruta: string; children: (datos: T) => ReactNode }) {
  const { data, isPending, error } = useDatos<T>(ruta)
  if (isPending) return <Cargando />
  if (data === undefined) return <ErrorCarga error={error} />
  return <>{children(data)}</>
}

/** Vacía los <input type="file"> tras subir, sin tocar el resto (form.reset() devolvería los textos a los valores viejos). */
export const limpiarArchivos = (form: HTMLFormElement) =>
  form.querySelectorAll<HTMLInputElement>('input[type=file]').forEach((i) => { i.value = '' })

/** onSubmit que evita la recarga y entrega el <form> (para leerForm o new FormData). */
export const alEnviar = (fn: (form: HTMLFormElement) => void) => (e: FormEvent<HTMLFormElement>) => {
  e.preventDefault()
  fn(e.currentTarget)
}

export function Pagina({ titulo, icono, descripcion, children }: { titulo: string; icono: string; descripcion?: string; children: ReactNode }) {
  return (
    <section className="space-y-6">
      <header>
        <h1 className="flex items-center gap-2 text-xl font-semibold text-zinc-900">
          <i className={`bi ${icono}`} aria-hidden /> {titulo}
        </h1>
        {descripcion && <p className="mt-1 text-sm text-zinc-500">{descripcion}</p>}
      </header>
      {children}
    </section>
  )
}

export function Cargando() {
  return <p className="text-sm text-zinc-500" role="status">Cargando…</p>
}

export function ErrorCarga({ error }: { error: Error | null }) {
  return <p className="rounded-lg bg-red-50 p-3 text-sm text-red-700" role="alert">{error?.message ?? 'No se pudo cargar.'}</p>
}

type CampoProps = InputHTMLAttributes<HTMLInputElement> & { label: string; ayuda?: string }

export function Campo({ label, ayuda, id, name, ...props }: CampoProps) {
  const idCampo = id ?? name
  return (
    <div>
      <label htmlFor={idCampo} className="etiqueta">{label}</label>
      <input id={idCampo} name={name} className="campo" {...props} />
      {ayuda && <p className="mt-1 text-xs text-zinc-500">{ayuda}</p>}
    </div>
  )
}

export function AreaTexto({ label, id, name, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement> & { label: string }) {
  const idCampo = id ?? name
  return (
    <div>
      <label htmlFor={idCampo} className="etiqueta">{label}</label>
      <textarea id={idCampo} name={name} rows={4} className="campo" {...props} />
    </div>
  )
}

/** Interruptor accesible (checkbox con apariencia de switch). */
export function Interruptor({ checked, onChange, label, name }: { checked?: boolean; onChange?: (v: boolean) => void; label: string; name?: string }) {
  return (
    <label className="inline-flex cursor-pointer items-center gap-2 text-sm text-zinc-700">
      <input
        type="checkbox"
        name={name}
        className="peer sr-only"
        {...(onChange ? { checked, onChange: (e) => onChange(e.target.checked) } : { defaultChecked: checked })}
      />
      <span className="relative h-5 w-9 rounded-full bg-zinc-300 transition peer-checked:bg-zinc-900 peer-focus-visible:ring-2 peer-focus-visible:ring-zinc-500 after:absolute after:top-0.5 after:left-0.5 after:h-4 after:w-4 after:rounded-full after:bg-white after:transition peer-checked:after:translate-x-4" />
      <span>{label}</span>
    </label>
  )
}

export function BotonGuardar({ pendiente, texto = 'Guardar cambios' }: { pendiente: boolean; texto?: string }) {
  return (
    <button type="submit" className="boton" disabled={pendiente}>
      <i className="bi bi-check2" aria-hidden /> {pendiente ? 'Guardando…' : texto}
    </button>
  )
}

export function Vacio({ children }: { children: ReactNode }) {
  return <p className="rounded-lg border border-dashed border-zinc-300 p-6 text-center text-sm text-zinc-500">{children}</p>
}

export function Pista({ children }: { children: ReactNode }) {
  return (
    <p className="text-xs text-zinc-500">
      <i className="bi bi-info-circle me-1" aria-hidden />
      {children}
    </p>
  )
}
