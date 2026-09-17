/**
 * Convierte un <textarea> de HTML plano en un editor visual (WYSIWYG) usando Quill.js,
 * con fallback automático al textarea normal si Quill no llegó a cargar (ej. CDN caído
 * o sin conexión) — en ese caso el formulario sigue funcionando igual que antes.
 *
 * Requiere que en la página ya estén cargados quill.snow.css y quill.min.js
 * (se cargan una sola vez desde admin/base_admin.html, no hace falta repetirlos).
 *
 * Uso en una plantilla hija:
 *
 *   <textarea class="form-control" name="contenido" id="contenido-textarea" rows="10" required>{{ valor }}</textarea>
 *   <div id="contenido-editor" style="display:none;"></div>
 *   <div id="contenido-error" class="text-danger small mt-1" style="display:none;">
 *       Este campo no puede quedar vacío.
 *   </div>
 *
 *   {% block extra_scripts %}
 *   <script>
 *       inicializarEditorEnriquecido({
 *           textareaId: 'contenido-textarea',
 *           editorId: 'contenido-editor',
 *           errorId: 'contenido-error',
 *           placeholder: 'Escribe aquí...'
 *       });
 *   </script>
 *   {% endblock %}
 */
function inicializarEditorEnriquecido(config) {
    document.addEventListener('DOMContentLoaded', function () {
        var textarea = document.getElementById(config.textareaId);
        var editorDiv = document.getElementById(config.editorId);
        var errorMsg = config.errorId ? document.getElementById(config.errorId) : null;

        // Si falta algún elemento o Quill no cargó, no hacemos nada:
        // el textarea normal sigue visible y funcional tal cual estaba.
        if (!textarea || !editorDiv || typeof Quill === 'undefined') {
            return;
        }

        var quill = new Quill(editorDiv, {
            theme: 'snow',
            placeholder: config.placeholder || '',
            modules: {
                toolbar: config.toolbar || [
                    [{ header: [2, 3, false] }],
                    ['bold', 'italic', 'underline'],
                    ['link'],
                    [{ list: 'ordered' }, { list: 'bullet' }],
                    ['clean']
                ]
            }
        });

        // Guardamos la instancia para poder actualizar su contenido más adelante
        // desde código externo (ver actualizarContenidoEditorEnriquecido), por
        // ejemplo cuando un mismo formulario/modal se reutiliza para editar
        // distintos registros y el textarea cambia de valor después de cargada
        // la página.
        window.__editoresEnriquecidos = window.__editoresEnriquecidos || {};
        window.__editoresEnriquecidos[config.textareaId] = quill;

        // Si el textarea ya traía contenido (modo edición), lo cargamos en el editor visual
        if (textarea.value.trim() !== '') {
            quill.clipboard.dangerouslyPasteHTML(textarea.value);
        }

        // Ocultamos el textarea plano y mostramos el editor visual en su lugar
        textarea.style.display = 'none';
        editorDiv.style.display = 'block';

        var form = textarea.closest('form');
        if (!form) return;

        // Mantenemos el textarea sincronizado en cada cambio, no solo al enviar,
        // así cualquier otra validación del formulario ve el contenido real.
        quill.on('text-change', function () {
            textarea.value = quill.root.innerHTML;
        });

        form.addEventListener('submit', function (e) {
            textarea.value = quill.root.innerHTML;

            var estaVacio = quill.getText().trim().length === 0;
            var esRequerido = config.requerido !== false;

            if (esRequerido && estaVacio) {
                // El atributo "required" del textarea no sirve aquí porque el campo
                // está oculto (display:none), y los navegadores ignoran la validación
                // nativa en campos ocultos. Por eso validamos manualmente.
                e.preventDefault();
                if (errorMsg) errorMsg.style.display = 'block';
            } else if (errorMsg) {
                errorMsg.style.display = 'none';
            }
        });
    });
}

/**
 * Actualiza el contenido de un editor ya inicializado con inicializarEditorEnriquecido().
 * Úsala cuando un mismo formulario o modal se reutiliza para editar distintos
 * registros (por ejemplo un modal "Editar X" que se llena con datos distintos
 * cada vez que se abre) — asignar textarea.value directamente NO actualiza el
 * editor visual de Quill porque este ya inicializó su contenido una sola vez
 * al cargar la página.
 *
 * Si Quill no llegó a cargar (fallback), actualiza el textarea normal.
 *
 * Uso:
 *   actualizarContenidoEditorEnriquecido('descripcion_edit', servicio.descripcion);
 */
function actualizarContenidoEditorEnriquecido(textareaId, contenidoHtml) {
    var quill = window.__editoresEnriquecidos && window.__editoresEnriquecidos[textareaId];
    var textarea = document.getElementById(textareaId);

    if (quill) {
        // Limpiamos el contenido anterior y pegamos el nuevo. El listener
        // 'text-change' ya registrado en inicializarEditorEnriquecido se
        // encarga de mantener sincronizado el textarea oculto.
        quill.setContents([]);
        if (contenidoHtml && contenidoHtml.trim() !== '') {
            quill.clipboard.dangerouslyPasteHTML(contenidoHtml);
        }
    } else if (textarea) {
        textarea.value = contenidoHtml || '';
    }
}