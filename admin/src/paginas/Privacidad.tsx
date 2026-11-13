import { api, leerForm, useAccion } from '../api'
import { alEnviar, BotonGuardar, Campo, ConDatos, Pagina } from '../componentes/ui'
import type { Legal, RegistroConsentimientos } from '../tipos'

const RUTA = '/api/admin/legal'

export function Privacidad() {
  const guardar = useAccion((datos: Record<string, string>) => api(RUTA, { method: 'PUT', json: datos }), [RUTA], 'Datos de privacidad guardados.')

  return (
    <Pagina titulo="Privacidad" icono="bi-shield-check" descripcion="Responsable de los datos personales, tal como aparece en la política de privacidad (Ley 21.719).">
      <ConDatos<Legal> ruta={RUTA}>
        {(l) => (
          <form className="tarjeta space-y-4" onSubmit={alEnviar((f) => guardar.mutate(leerForm(f)))}>
            <Campo label="Razón social o nombre del responsable" name="razon_social" defaultValue={l.razon_social ?? ''} required />
            <Campo label="RUT" name="rut" defaultValue={l.rut ?? ''} placeholder="12.345.678-9" maxLength={20} />
            <Campo label="Correo para temas de privacidad" name="email_privacidad" type="email" defaultValue={l.email_privacidad ?? ''}
              ayuda="Donde las personas ejercen sus derechos (acceso, eliminación, etc.). Si lo dejas vacío se usa el correo de Contacto." />
            <p className="text-sm">
              <a href="/privacidad" target="_blank" rel="noopener" className="text-zinc-700 underline hover:text-zinc-900">
                Ver la política publicada <i className="bi bi-box-arrow-up-right" aria-hidden />
              </a>
            </p>
            <BotonGuardar pendiente={guardar.isPending} />
          </form>
        )}
      </ConDatos>

      <ConDatos<RegistroConsentimientos> ruta={`${RUTA}/consentimientos`}>{(r) => <Registro r={r} />}</ConDatos>
    </Pagina>
  )
}

const DECISIONES: [string, string][] = [['aceptado', 'Aceptaron'], ['rechazado', 'Rechazaron'], ['retirado', 'Retiraron'], ['eliminado', 'Pidieron borrar sus datos']]

/** Registro de consentimientos: prueba de cuándo y cómo se decidió, sin datos personales (solo un id aleatorio). */
function Registro({ r }: { r: RegistroConsentimientos }) {
  return (
    <section className="tarjeta space-y-4" aria-labelledby="titulo-registro">
      <div>
        <h2 id="titulo-registro" className="font-medium text-zinc-900">Registro de consentimientos</h2>
        <p className="text-xs text-zinc-500">Cada decisión del banner queda anotada con fecha, versión de la política y un id aleatorio, sin datos personales.</p>
      </div>
      <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {DECISIONES.map(([clave, texto]) => (
          <div key={clave} className="rounded-lg bg-zinc-50 p-3">
            <dt className="text-xs text-zinc-500">{texto}</dt>
            <dd className="text-xl font-semibold text-zinc-900 tabular-nums">{r.ultimos_30_dias[clave] ?? 0}</dd>
          </div>
        ))}
      </dl>
      <p className="text-xs text-zinc-500">Últimos 30 días.</p>
      {r.recientes.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <caption className="sr-only">Últimas 20 decisiones</caption>
            <thead className="text-left text-xs text-zinc-500">
              <tr><th className="py-1 pe-4 font-medium">Fecha</th><th className="pe-4 font-medium">Decisión</th><th className="pe-4 font-medium">Versión</th><th className="font-medium">Referencia</th></tr>
            </thead>
            <tbody>
              {r.recientes.map((c) => (
                <tr key={c.referencia} className="border-t border-zinc-100">
                  <td className="py-1.5 pe-4 tabular-nums">{new Date(c.fecha).toLocaleString('es-CL', { dateStyle: 'short', timeStyle: 'short' })}</td>
                  <td className="pe-4">{c.decision}</td>
                  <td className="pe-4">{c.version}</td>
                  <td className="font-mono text-xs text-zinc-500">{c.referencia.slice(0, 12)}…</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
