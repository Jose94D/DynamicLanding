import { CategoryScale, Chart, Filler, LinearScale, LineController, LineElement, PointElement, Tooltip } from 'chart.js'
import { useEffect, useRef, useState } from 'react'
import { ConDatos, Pagina } from '../componentes/ui'
import type { Analiticas as AnaliticasT, Serie } from '../tipos'

Chart.register(LineController, LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Filler)

const VISTAS = { por_semana: 'Por semana', por_mes: 'Por mes', por_anio: 'Por año' } as const
type Vista = keyof typeof VISTAS

export function Analiticas() {
  return (
    <Pagina titulo="Analíticas" icono="bi-bar-chart-fill" descripcion="Visitas a las páginas públicas del sitio.">
      <ConDatos<AnaliticasT> ruta="/api/admin/analiticas">{(a) => <Contenido a={a} />}</ConDatos>
    </Pagina>
  )
}

function Contenido({ a }: { a: AnaliticasT }) {
  const [vista, setVista] = useState<Vista>('por_mes')
  const tarjetas = [['Esta semana', a.semana_actual], ['Este mes', a.mes_actual], ['Este año', a.anio_actual], ['Desde el lanzamiento', a.total]] as const

  return (
    <>
      <dl className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {tarjetas.map(([titulo, valor]) => (
          <div key={titulo} className="tarjeta">
            <dt className="text-xs text-zinc-500">{titulo}</dt>
            <dd className="mt-1 text-2xl font-semibold text-zinc-900 tabular-nums">{valor.toLocaleString('es-CL')}</dd>
          </div>
        ))}
      </dl>

      <div className="tarjeta space-y-4">
        <div role="tablist" aria-label="Agrupar visitas" className="inline-flex rounded-lg bg-zinc-100 p-1">
          {(Object.keys(VISTAS) as Vista[]).map((v) => (
            <button key={v} role="tab" aria-selected={vista === v} onClick={() => setVista(v)}
              className={`rounded-md px-3 py-1 text-sm ${vista === v ? 'bg-white font-medium text-zinc-900 shadow-sm' : 'text-zinc-600'}`}>
              {VISTAS[v]}
            </button>
          ))}
        </div>
        {a[vista].length ? <Grafico serie={a[vista]} titulo={`Visitas ${VISTAS[vista].toLowerCase()}`} /> : <p className="text-sm text-zinc-500">Aún no hay visitas registradas.</p>}
      </div>
    </>
  )
}

function Grafico({ serie, titulo }: { serie: Serie[]; titulo: string }) {
  const lienzo = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const grafico = new Chart(lienzo.current!, {
      type: 'line',
      data: {
        labels: serie.map((s) => s.periodo),
        datasets: [{ label: 'Visitas', data: serie.map((s) => s.total), borderColor: '#18181b', backgroundColor: 'rgba(24,24,27,0.08)', fill: true, tension: 0.3 }],
      },
      options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, ticks: { precision: 0 } } } },
    })
    return () => grafico.destroy()
  }, [serie])

  return (
    <div className="h-72">
      <canvas ref={lienzo} role="img" aria-label={`${titulo}: ${serie.map((s) => `${s.periodo} ${s.total}`).join(', ')}`} />
    </div>
  )
}
