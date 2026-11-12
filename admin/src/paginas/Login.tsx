import { useMutation, useQueryClient } from '@tanstack/react-query'
import type { FormEvent } from 'react'
import { api, fijarCsrf, leerForm, RUTA_SESION } from '../api'
import { Campo } from '../componentes/ui'
import type { Sesion } from '../tipos'

export function Login() {
  const qc = useQueryClient()
  const login = useMutation({
    mutationFn: (datos: Record<string, string>) => api<Sesion>('/api/auth/login', { method: 'POST', json: datos }),
    onSuccess: (sesion) => {
      fijarCsrf(sesion.csrf_token)
      qc.setQueryData([RUTA_SESION], sesion)
    },
  })

  function enviar(e: FormEvent<HTMLFormElement>) {
    e.preventDefault()
    login.mutate(leerForm(e.currentTarget))
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-zinc-100 p-4">
      <form onSubmit={enviar} className="tarjeta w-full max-w-sm space-y-4">
        <img src="/admin/logo-black.png" alt="DynamicLanding CMS" className="mx-auto h-10" />
        <h1 className="text-center text-lg font-semibold text-zinc-900">Panel de administración</h1>
        {login.error && <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{login.error.message}</p>}
        <Campo label="Usuario" name="username" autoComplete="username" required autoFocus />
        <Campo label="Contraseña" name="password" type="password" autoComplete="current-password" required />
        <button className="boton w-full" disabled={login.isPending}>{login.isPending ? 'Entrando…' : 'Iniciar sesión'}</button>
      </form>
    </main>
  )
}
