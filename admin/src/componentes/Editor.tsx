import Quill from 'quill'
import 'quill/dist/quill.snow.css'
import { useEffect, useRef } from 'react'

/**
 * Editor enriquecido (Quill 2). No controlado: recibe el HTML inicial y avisa cada cambio.
 * La misma barra que tenía el panel Flask; el backend sanea el HTML al mostrarlo (limpiar_html).
 */
export function Editor({ inicial, onChange, etiqueta }: { inicial: string; onChange: (html: string) => void; etiqueta: string }) {
  const contenedor = useRef<HTMLDivElement>(null)
  const alCambiar = useRef(onChange)
  useEffect(() => { alCambiar.current = onChange })

  useEffect(() => {
    const nodo = contenedor.current!
    const div = nodo.appendChild(document.createElement('div'))
    const quill = new Quill(div, {
      theme: 'snow',
      placeholder: 'Escribe aquí…',
      modules: {
        toolbar: [[{ header: [2, 3, false] }], ['bold', 'italic', 'underline'], ['link'], [{ list: 'ordered' }, { list: 'bullet' }], ['clean']],
      },
    })
    quill.clipboard.dangerouslyPasteHTML(inicial)
    quill.root.setAttribute('aria-label', etiqueta)
    quill.on('text-change', () => alCambiar.current(quill.getText().trim() ? quill.root.innerHTML : ''))
    return () => { nodo.innerHTML = '' }  // StrictMode monta dos veces: no duplicar la barra
  }, []) // solo al montar: 'inicial' es el valor de partida, no se re-sincroniza

  return <div ref={contenedor} />
}
