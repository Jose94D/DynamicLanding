import { api, leerForm, useAccion } from '../api'
import { alEnviar, BotonGuardar, Campo, Pagina } from '../componentes/ui'

export function Password() {
  const cambiar = useAccion(
    (datos: Record<string, string>) => api('/api/auth/cambiar-password', { method: 'POST', json: datos }),
    [],
    'Contraseña actualizada.',
  )

  return (
    <Pagina titulo="Cambiar contraseña" icono="bi-key-fill">
      <form className="tarjeta max-w-md space-y-4" onSubmit={alEnviar((f) => cambiar.mutate(leerForm(f), { onSuccess: () => f.reset() }))}>
        <Campo label="Contraseña actual" name="actual" type="password" autoComplete="current-password" required />
        <Campo label="Nueva contraseña" name="nueva" type="password" autoComplete="new-password" minLength={8} required ayuda="Mínimo 8 caracteres." />
        <Campo label="Repite la nueva contraseña" name="confirmar" type="password" autoComplete="new-password" minLength={8} required />
        <BotonGuardar pendiente={cambiar.isPending} texto="Cambiar contraseña" />
      </form>
    </Pagina>
  )
}
