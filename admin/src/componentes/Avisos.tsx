import { createContext, useCallback, useContext, useState, type ReactNode } from 'react'

type Tipo = 'ok' | 'error'
type Aviso = { id: number; texto: string; tipo: Tipo }

const Contexto = createContext<(texto: string, tipo?: Tipo) => void>(() => {})

export const useAviso = () => useContext(Contexto)

/** Avisos flotantes (reemplazan a los flash de Flask). Se cierran solos a los 4 segundos. */
export function AvisosProvider({ children }: { children: ReactNode }) {
  const [avisos, setAvisos] = useState<Aviso[]>([])

  const avisar = useCallback((texto: string, tipo: Tipo = 'ok') => {
    const id = Date.now() + Math.random()
    setAvisos((a) => [...a, { id, texto, tipo }])
    setTimeout(() => setAvisos((a) => a.filter((x) => x.id !== id)), 4000)
  }, [])

  return (
    <Contexto.Provider value={avisar}>
      {children}
      <div aria-live="polite" className="fixed right-4 bottom-4 z-50 flex w-80 max-w-[calc(100vw-2rem)] flex-col gap-2">
        {avisos.map((a) => (
          <div
            key={a.id}
            role={a.tipo === 'error' ? 'alert' : 'status'}
            className={`rounded-lg px-4 py-3 text-sm shadow-lg ${a.tipo === 'error' ? 'bg-red-600 text-white' : 'bg-zinc-900 text-white'}`}
          >
            <i className={`bi ${a.tipo === 'error' ? 'bi-exclamation-circle' : 'bi-check-circle'} me-2`} />
            {a.texto}
          </div>
        ))}
      </div>
    </Contexto.Provider>
  )
}
