import { useState } from 'react'
import { api, leerForm, useAccion, useReordenar } from '../api'
import { ListaOrdenable } from '../componentes/ListaOrdenable'
import { alEnviar, BotonGuardar, Campo, ConDatos, Interruptor, Pagina, Pista } from '../componentes/ui'
import type { Contacto as ContactoT, Modulo } from '../tipos'

const RUTA = '/api/admin/contacto'

export function Contacto() {
  return (
    <Pagina titulo="Contáctanos" icono="bi-envelope-paper" descripcion="Formulario, mapa y datos de contacto.">
      <ConDatos<ContactoT> ruta={RUTA}>{(c) => <Formulario contacto={c} />}</ConDatos>
    </Pagina>
  )
}

function Formulario({ contacto }: { contacto: ContactoT }) {
  const [visibles, setVisibles] = useState(() => Object.fromEntries(contacto.submodulos.map((s) => [s.id, s.activo])))
  const reordenar = useReordenar<Modulo>(RUTA, `${RUTA}/submodulos/orden`, 'submodulos')
  const guardar = useAccion(
    (form: HTMLFormElement) => {
      const { direccion, ...datos } = leerForm(form)
      const submodulos = Object.entries(visibles).map(([id, activo]) => ({ id, activo }))
      return api(RUTA, { method: 'PUT', json: { datos, direccion, submodulos } })
    },
    [RUTA],
    'Sección Contáctanos actualizada.',
  )
  const d = contacto.datos

  return (
    <form className="space-y-6" onSubmit={alEnviar((f) => guardar.mutate(f))}>
      <div className="tarjeta space-y-3">
        <h2 className="font-medium text-zinc-900">Partes de la sección</h2>
        <ListaOrdenable items={contacto.submodulos} onOrdenar={reordenar}>
          {(s, asa) => (
            <div className="flex items-center gap-3 rounded-lg border border-zinc-200 px-3 py-2">
              {asa}
              <span className="flex-1 text-sm">{s.nombre_legible}</span>
              <Interruptor label={visibles[s.id] ? 'Visible' : 'Oculto'} checked={visibles[s.id]} onChange={(v) => setVisibles({ ...visibles, [s.id]: v })} />
            </div>
          )}
        </ListaOrdenable>
        <Pista>El orden se guarda al soltar; la visibilidad, con el botón de abajo.</Pista>
      </div>

      <div className="tarjeta grid gap-4 sm:grid-cols-2">
        <Campo label="Título" name="titulo" defaultValue={d.titulo} required />
        <Campo label="Subtítulo" name="subtitulo" defaultValue={d.subtitulo ?? ''} />
        <Campo label="Teléfono" name="telefono" type="tel" defaultValue={d.telefono ?? ''} />
        <Campo label="Correo" name="email" type="email" defaultValue={d.email ?? ''} />
        <Campo label="Ubicación (texto)" name="ubicacion_texto" defaultValue={d.ubicacion_texto ?? ''} />
        <Campo label="Horario" name="horario" defaultValue={d.horario ?? ''} />
        <div className="sm:col-span-2">
          <Campo label="Dirección del mapa" name="direccion" defaultValue={contacto.direccion} required ayuda="La que se busca en Google Maps para el mapa embebido." />
        </div>
      </div>
      <BotonGuardar pendiente={guardar.isPending} />
    </form>
  )
}
