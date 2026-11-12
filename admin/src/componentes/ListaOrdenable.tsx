import {
  closestCenter, DndContext, KeyboardSensor, PointerSensor, useSensor, useSensors, type DragEndEvent,
} from '@dnd-kit/core'
import {
  arrayMove, rectSortingStrategy, SortableContext, sortableKeyboardCoordinates, useSortable, verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'
import type { ReactNode } from 'react'

type Id = string | number

type Props<T extends { id: Id }> = {
  items: T[]
  onOrdenar: (items: T[]) => void
  /** Renderiza cada elemento; `asa` es el botón para arrastrar (también funciona con teclado: espacio + flechas). */
  children: (item: T, asa: ReactNode) => ReactNode
  grilla?: boolean
}

/** Lista reordenable con drag & drop (reemplaza a SortableJS del panel Flask). */
export function ListaOrdenable<T extends { id: Id }>({ items, onOrdenar, children, grilla }: Props<T>) {
  const sensores = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  )

  function alSoltar({ active, over }: DragEndEvent) {
    if (!over || active.id === over.id) return
    const desde = items.findIndex((i) => i.id === active.id)
    const hasta = items.findIndex((i) => i.id === over.id)
    onOrdenar(arrayMove(items, desde, hasta))
  }

  return (
    <DndContext sensors={sensores} collisionDetection={closestCenter} onDragEnd={alSoltar}>
      <SortableContext items={items.map((i) => i.id)} strategy={grilla ? rectSortingStrategy : verticalListSortingStrategy}>
        <ul className={grilla ? 'grid grid-cols-2 gap-3 sm:grid-cols-3' : 'space-y-2'}>
          {items.map((item) => (
            <Fila key={item.id} id={item.id}>{(asa) => children(item, asa)}</Fila>
          ))}
        </ul>
      </SortableContext>
    </DndContext>
  )
}

function Fila({ id, children }: { id: Id; children: (asa: ReactNode) => ReactNode }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id })
  const asa = (
    <button
      type="button"
      {...attributes}
      {...listeners}
      aria-label="Arrastrar para reordenar"
      className="cursor-grab rounded p-1 text-zinc-400 hover:text-zinc-700 focus-visible:ring-2 focus-visible:ring-zinc-500 focus-visible:outline-none active:cursor-grabbing"
    >
      <i className="bi bi-grip-vertical" aria-hidden />
    </button>
  )
  return (
    <li
      ref={setNodeRef}
      style={{ transform: CSS.Transform.toString(transform), transition }}
      className={isDragging ? 'relative z-10 opacity-70' : undefined}
    >
      {children(asa)}
    </li>
  )
}
