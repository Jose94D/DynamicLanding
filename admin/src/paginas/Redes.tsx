import { api, leerForm, useAccion } from '../api'
import { alEnviar, BotonGuardar, Campo, ConDatos, Interruptor, Pagina } from '../componentes/ui'
import type { Red } from '../tipos'

const RUTA = '/api/admin/redes'

export function Redes() {
  const guardar = useAccion(
    ({ plataforma, form }: { plataforma: string; form: HTMLFormElement }) => {
      const { access_token, account_id } = leerForm(form)
      const activo_api = (form.elements.namedItem('activo_api') as HTMLInputElement).checked
      // Token vacío = conservar el guardado (la API nunca lo devuelve, así que no se puede precargar).
      return api(`${RUTA}/${plataforma}`, { method: 'PUT', json: { account_id, activo_api, access_token: access_token || null } })
    },
    [RUTA],
    'Configuración guardada.',
  )

  return (
    <Pagina titulo="Redes sociales" icono="bi-instagram" descripcion="Conecta Instagram para mostrar tu última publicación.">
      <ConDatos<Red[]> ruta={RUTA}>
        {(redes) => redes.map((r) => (
          <form key={r.plataforma} className="tarjeta space-y-4" onSubmit={alEnviar((form) => guardar.mutate({ plataforma: r.plataforma, form }))}>
            <h2 className="font-medium capitalize text-zinc-900">{r.plataforma}</h2>
            <Campo label="ID de la cuenta" name="account_id" defaultValue={r.account_id ?? ''} />
            <Campo
              label="Token de acceso"
              name="access_token"
              type="password"
              autoComplete="off"
              placeholder={r.tiene_token ? '•••••••• (guardado; déjalo vacío para conservarlo)' : ''}
            />
            <Interruptor name="activo_api" label="Mostrar en la landing" checked={r.activo_api} />
            <div><BotonGuardar pendiente={guardar.isPending} /></div>
          </form>
        ))}
      </ConDatos>
    </Pagina>
  )
}
