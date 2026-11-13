import { CategoryScale, Chart, Filler, LinearScale, LineController, LineElement, PointElement, Tooltip } from 'chart.js'
import { useEffect, useRef, useState } from 'react'
import { ConDatos, Pagina } from '../componentes/ui'
import type { Analiticas as AnaliticasT, Conteo, Serie } from '../tipos'

Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Filler)

const PERIODOS = [[7, '7 días'], [30, '30 días'], [90, '90 días'], [365, '12 meses']] as const
const ORIGENES: Record<string, string> = { directo: 'Directo', buscador: 'Buscadores', social: 'Redes sociales', referido: 'Otros sitios', 'campaña': 'Campañas (UTM)' }
const DISPOSITIVOS: Record<string, string> = { movil: 'Celular', tablet: 'Tablet', escritorio: 'Escritorio' }
const numero = (n: number) => n.toLocaleString('es-CL')
const duracion = (s: number) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')} min`

/** '2026-10-15' -> '15 oct'; '2026-10' -> 'oct 2026'. Se arma a mano para no depender de la zona horaria. */
function etiqueta(periodo: string) {
  const [anio, mes, dia] = periodo.split('-').map(Number)
  const nombreMes = new Date(2000, mes - 1, 1).toLocaleString('es-CL', { month: 'short' }).replace('.', '')
  return dia ? `${dia} ${nombreMes}` : `${nombreMes} ${anio}`
}

export function Analiticas() {
  const [dias, setDias] = useState(30)

  return (
    <Pagina titulo="Analíticas" icono="bi-bar-chart-fill" descripcion="Visitas a las páginas públicas del sitio.">
      <div role="tablist" aria-label="Período" className="inline-flex rounded-lg bg-zinc-200/70 p-1">
        {PERIODOS.map(([d, texto]) => (
          <button key={d} role="tab" aria-selected={dias === d} onClick={() => setDias(d)}
            className={`rounded-md px-3 py-1 text-sm ${dias === d ? 'bg-white font-medium text-zinc-900 shadow-sm' : 'text-zinc-600 hover:text-zinc-900'}`}>
            {texto}
          </button>
        ))}
      </div>
      <ConDatos<AnaliticasT> key={dias} ruta={`/api/admin/analiticas?dias=${dias}`}>{(a) => <Contenido a={a} />}</ConDatos>
    </Pagina>
  )
}

/** Variación contra el período anterior. Las tasas (%) se comparan en puntos; el resto, en % de cambio. */
function variacion(actual: number, anterior: number, puntos = false) {
  if (actual === anterior) return { texto: 'Igual que el período anterior', clase: 'text-zinc-500' }
  if (!puntos && anterior === 0) return { texto: 'Sin datos en el período anterior', clase: 'text-zinc-500' }
  const delta = puntos ? actual - anterior : ((actual - anterior) / anterior) * 100
  const valor = `${delta > 0 ? '+' : ''}${delta.toLocaleString('es-CL', { maximumFractionDigits: 1 })}${puntos ? ' pts' : '%'}`
  return { texto: `${valor} vs. período anterior`, clase: delta > 0 ? 'text-emerald-700' : 'text-red-700' }
}

function Tarjeta({ titulo, valor, detalle, actual, anterior, puntos }: {
  titulo: string; valor: number | string; detalle?: string; actual?: number; anterior?: number; puntos?: boolean
}) {
  const v = actual !== undefined && anterior !== undefined ? variacion(actual, anterior, puntos) : null
  return (
    <div className="tarjeta">
      <dt className="text-xs text-zinc-500">{titulo}</dt>
      <dd className="mt-1 text-2xl font-semibold text-zinc-900 tabular-nums">{typeof valor === 'number' ? numero(valor) : valor}</dd>
      {v && <dd className={`mt-1 text-xs font-medium ${v.clase}`}>{v.texto}</dd>}
      {detalle && <dd className="mt-1 text-xs text-zinc-500">{detalle}</dd>}
    </div>
  )
}

function Contenido({ a }: { a: AnaliticasT }) {
  const c = a.consentidas
  const ant = a.anterior.consentidas
  const porcentaje = (parte: number) => (c.visitantes_unicos ? `${Math.round((parte / c.visitantes_unicos) * 100)}%` : '—')

  return (
    <>
      <section className="space-y-3" aria-labelledby="titulo-todas">
        <h2 id="titulo-todas" className="text-sm font-medium text-zinc-700">Todas las visitas</h2>
        <div className="grid gap-3 lg:grid-cols-[13rem_1fr]">
          <dl className="grid content-start gap-3">
            <Tarjeta titulo="Páginas vistas" valor={a.paginas_vistas} actual={a.paginas_vistas} anterior={a.anterior.paginas_vistas} detalle="Incluye a quienes rechazaron cookies" />
            <Tarjeta titulo="Mensajes recibidos" valor={a.mensajes_recibidos} actual={a.mensajes_recibidos} anterior={a.anterior.mensajes_recibidos} detalle="Desde el formulario de contacto" />
          </dl>
          <div className="tarjeta min-w-0">
            {a.paginas_vistas ? <Grafico serie={a.serie} titulo={`Páginas vistas en los últimos ${a.dias === 365 ? '12 meses' : `${a.dias} días`}`} />
              : <p className="text-sm text-zinc-500">Aún no hay visitas en este período.</p>}
          </div>
        </div>
      </section>

      <section className="space-y-3" aria-labelledby="titulo-consentidas">
        <div>
          <h2 id="titulo-consentidas" className="text-sm font-medium text-zinc-700">Visitantes que aceptaron cookies</h2>
          <p className="text-xs text-zinc-500">
            Estas métricas solo cuentan a quienes aceptaron las cookies analíticas; quienes las rechazan no se pueden seguir (Ley 21.719).
          </p>
        </div>
        <dl className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          <Tarjeta titulo="Visitas" valor={c.visitas} actual={c.visitas} anterior={ant.visitas} detalle={`${numero(c.paginas_vistas)} páginas vistas`} />
          <Tarjeta titulo="Visitantes únicos" valor={c.visitantes_unicos} actual={c.visitantes_unicos} anterior={ant.visitantes_unicos} />
          <Tarjeta titulo="Nuevos" valor={c.nuevos} actual={c.nuevos} anterior={ant.nuevos} detalle={`${porcentaje(c.nuevos)} de los visitantes`} />
          <Tarjeta titulo="Recurrentes" valor={c.recurrentes} actual={c.recurrentes} anterior={ant.recurrentes} detalle={`${porcentaje(c.recurrentes)} de los visitantes`} />
        </dl>
        <dl className="grid gap-3 sm:grid-cols-3">
          <Tarjeta titulo="Conversión del formulario" valor={`${c.tasa_conversion.toLocaleString('es-CL')}%`} actual={c.tasa_conversion} anterior={ant.tasa_conversion} puntos
            detalle={`${numero(c.visitas_con_envio)} de ${numero(c.visitas)} visitas enviaron un mensaje`} />
          <Tarjeta titulo="Duración media de la visita" valor={duracion(c.duracion_media)} actual={c.duracion_media} anterior={ant.duracion_media} detalle="Tiempo con la página visible" />
          <Tarjeta titulo="Galería" valor={c.aperturas_galeria} actual={c.aperturas_galeria} anterior={ant.aperturas_galeria}
            detalle={`imágenes abiertas en ${numero(c.visitas_con_galeria)} visitas · ${numero(c.navegaciones_galeria)} usos de las flechas`} />
        </dl>
        <div className="grid gap-3 lg:grid-cols-3">
          <Desglose titulo="Origen" filas={c.por_origen} nombres={ORIGENES} />
          <Desglose titulo="Dispositivo" filas={c.por_dispositivo} nombres={DISPOSITIVOS} />
          <Desglose titulo="Navegador" filas={c.por_navegador} />
        </div>
      </section>
    </>
  )
}

/** Lista con barras proporcionales: más legible que un gráfico de torta para 3 a 8 categorías. */
function Desglose({ titulo, filas, nombres = {} }: { titulo: string; filas: Conteo[]; nombres?: Record<string, string> }) {
  const total = filas.reduce((s, f) => s + f.total, 0)
  return (
    <div className="tarjeta">
      <h3 className="mb-3 text-sm font-medium text-zinc-900">{titulo}</h3>
      {total ? (
        <ul className="space-y-2.5">
          {filas.map((f) => {
            const pct = Math.round((f.total / total) * 100)
            return (
              <li key={f.nombre} className="text-sm">
                <div className="flex justify-between gap-2">
                  <span className="text-zinc-700">{nombres[f.nombre] ?? f.nombre}</span>
                  <span className="text-zinc-500 tabular-nums">{numero(f.total)} · {pct}%</span>
                </div>
                <div className="mt-1 h-1.5 rounded-full bg-zinc-100" aria-hidden>
                  <div className="h-full rounded-full bg-zinc-800" style={{ width: `${pct}%` }} />
                </div>
              </li>
            )
          })}
        </ul>
      ) : <p className="text-sm text-zinc-500">Sin datos en este período.</p>}
    </div>
  )
}

function Grafico({ serie, titulo }: { serie: Serie[]; titulo: string }) {
  const lienzo = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const grafico = new Chart(lienzo.current!, {
      type: 'line',
      data: {
        labels: serie.map((s) => etiqueta(s.periodo)),
        datasets: [{ label: 'Páginas vistas', data: serie.map((s) => s.total), borderColor: '#18181b', backgroundColor: 'rgba(24,24,27,0.08)', fill: true, tension: 0.3, pointRadius: serie.length > 40 ? 0 : 3 }],
      },
      options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
    })
    return () => grafico.destroy()
  }, [serie])

  return (
    <div className="h-64">
      <canvas ref={lienzo} role="img" aria-label={`${titulo}. Total: ${serie.reduce((s, x) => s + x.total, 0)}.`} />
    </div>
  )
}
