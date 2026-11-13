// Espejo de backend/app/schemas.py (las respuestas de la API).

export type Sesion = { usuario: string | null; csrf_token: string; mensajes_no_leidos: number }

export type Modulo = { id: string; nombre_legible: string; activo: boolean; orden: number }

export type Hero = { titulo: string; subtitulo: string | null; texto_boton: string | null; url_boton: string | null }

export type About = { titulo: string; descripcion: string | null; mision: string | null; nombre_archivo: string | null; bloques: Modulo[] }

export type ContactDatos = {
  titulo: string; subtitulo: string | null; telefono: string | null; email: string | null
  ubicacion_texto: string | null; horario: string | null
}
export type Contacto = { datos: ContactDatos; direccion: string; submodulos: Modulo[] }

export type Seo = { meta_titulo: string; meta_descripcion: string; og_image: string | null }

export type Red = { plataforma: string; account_id: string | null; activo_api: boolean; tiene_token: boolean }

export type Imagen = { id: number; nombre_archivo: string; orden: number }
export type ImagenGaleria = Imagen & { titulo: string | null }

export type Servicio = { id: number; icono: string; titulo: string; descripcion: string; orden: number }

export type Testimonio = {
  id: number; nombre: string; cargo: string | null; texto: string; foto: string | null; calificacion: number; orden: number
}

export type ArticuloResumen = { id: number; titulo: string; slug: string; extracto: string; fecha_publicacion: string | null; activo: boolean }
export type Articulo = ArticuloResumen & { contenido: string }

export type Mensaje = { id: number; nombre: string; email: string; mensaje: string; fecha_envio: string; leido: boolean }

export type Serie = { periodo: string; total: number }
export type Conteo = { nombre: string; total: number }
type NumerosConsentidas = {
  visitas: number; visitantes_unicos: number; nuevos: number; recurrentes: number; paginas_vistas: number
  visitas_con_envio: number; tasa_conversion: number
  duracion_media: number; aperturas_galeria: number; navegaciones_galeria: number; visitas_con_galeria: number
}
type Numeros = { paginas_vistas: number; mensajes_recibidos: number; consentidas: NumerosConsentidas }
export type Analiticas = Numeros & {
  dias: number; desde: string; hasta: string
  serie: Serie[]
  consentidas: NumerosConsentidas & { por_origen: Conteo[]; por_dispositivo: Conteo[]; por_navegador: Conteo[] }
  anterior: Numeros
}

export type Legal = { razon_social: string | null; rut: string | null; email_privacidad: string | null }

export type RegistroConsentimientos = {
  ultimos_30_dias: Record<string, number>
  recientes: { fecha: string; decision: string; version: string; referencia: string }[]
}
