import { useState } from 'react'
import { api, useAccion } from '../api'
import { ListaOrdenable } from '../componentes/ListaOrdenable'
import { BotonGuardar, ConDatos, Interruptor, Pagina, Pista } from '../componentes/ui'
import type { Modulo } from '../tipos'

const RUTA = '/api/admin/modulos'

export function Modulos() {
  return (
    <Pagina titulo="Diseño y visibilidad" icono="bi-grid-1x2-fill" descripcion="Elige qué secciones muestra la landing y en qué orden.">
      <ConDatos<Modulo[]> ruta={RUTA}>{(modulos) => <Formulario inicial={modulos} />}</ConDatos>
    </Pagina>
  )
}

function Formulario({ inicial }: { inicial: Modulo[] }) {
  const [modulos, setModulos] = useState(inicial)
  const guardar = useAccion(
    () => api(RUTA, { method: 'PUT', json: modulos.map((m, i) => ({ id: m.id, activo: m.activo, orden: i + 1 })) }),
    [RUTA],
    'Configuración de módulos guardada.',
  )
  const alternar = (id: string, activo: boolean) => setModulos((ms) => ms.map((m) => (m.id === id ? { ...m, activo } : m)))

  return (
    <form className="tarjeta space-y-4" onSubmit={(e) => { e.preventDefault(); guardar.mutate() }}>
      <ListaOrdenable items={modulos} onOrdenar={setModulos}>
        {(m, asa) => (
          <div className="flex items-center gap-3 rounded-lg border border-zinc-200 bg-white px-3 py-2">
            {asa}
            <span className={`flex-1 text-sm ${m.activo ? 'text-zinc-900' : 'text-zinc-400 line-through'}`}>{m.nombre_legible}</span>
            <Interruptor label={m.activo ? 'Visible' : 'Oculto'} checked={m.activo} onChange={(v) => alternar(m.id, v)} />
          </div>
        )}
      </ListaOrdenable>
      <Pista>Arrastra desde el ícono para cambiar el orden. Los cambios se aplican al guardar.</Pista>
      <BotonGuardar pendiente={guardar.isPending} />
    </form>
  )
}
