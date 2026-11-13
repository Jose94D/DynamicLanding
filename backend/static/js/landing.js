/**
 * JS de la landing pública (reemplaza a Bootstrap JS). Sin dependencias.
 * - Pistas horizontales: botones [data-mover="-1|1"] y [data-ir="n"] con data-pista="<id de la pista>".
 * - Carrusel [data-carrusel]: marca el punto actual y avanza solo cada data-intervalo ms.
 * - Visor de imágenes: enlaces [data-visor="<id del dialog>"] abren la imagen en un <dialog>.
 * - Archivo del blog: resalta en la barra lateral el mes que se está leyendo.
 */
(function () {
  'use strict';

  var reducirMovimiento = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---------- Pistas horizontales ----------
  function paso(pista) {
    var item = pista.firstElementChild;
    var gap = parseFloat(getComputedStyle(pista).columnGap) || 0;
    return item ? item.offsetWidth + gap : pista.clientWidth;
  }

  // Al llegar a un extremo vuelve al otro, así las flechas nunca quedan "muertas".
  function mover(pista, dir) {
    var alFinal = pista.scrollLeft + pista.clientWidth >= pista.scrollWidth - 2;
    var alInicio = pista.scrollLeft <= 2;
    if (dir > 0 && alFinal) pista.scrollTo({ left: 0 });
    else if (dir < 0 && alInicio) pista.scrollTo({ left: pista.scrollWidth });
    else pista.scrollBy({ left: dir * paso(pista) });
  }

  document.addEventListener('click', function (e) {
    var boton = e.target.closest('[data-mover], [data-ir]');
    if (!boton) return;
    var pista = document.getElementById(boton.dataset.pista);
    if (!pista) return;
    if (boton.dataset.mover) mover(pista, Number(boton.dataset.mover));
    else pista.scrollTo({ left: Number(boton.dataset.ir) * pista.clientWidth });
  });

  // ---------- Carrusel ----------
  document.querySelectorAll('[data-carrusel]').forEach(function (carrusel) {
    var pista = carrusel.querySelector('.pista');
    var puntos = carrusel.querySelectorAll('[data-ir]');
    if (!pista || !puntos.length) return;

    function marcar() {
      var actual = Math.round(pista.scrollLeft / pista.clientWidth);
      puntos.forEach(function (p, i) { p.setAttribute('aria-current', String(i === actual)); });
    }
    pista.addEventListener('scroll', function () { requestAnimationFrame(marcar); }, { passive: true });
    marcar();

    var intervalo = Number(carrusel.dataset.intervalo);
    if (!intervalo || reducirMovimiento) return;
    // Se pausa con el mouse encima o con el foco dentro, para poder leer/usar los controles.
    var pausado = false;
    ['mouseenter', 'focusin'].forEach(function (ev) { carrusel.addEventListener(ev, function () { pausado = true; }); });
    ['mouseleave', 'focusout'].forEach(function (ev) { carrusel.addEventListener(ev, function () { pausado = false; }); });
    setInterval(function () { if (!pausado && !document.hidden) mover(pista, 1); }, intervalo);
  });

  // ---------- Visor de imágenes ----------
  document.addEventListener('click', function (e) {
    var enlace = e.target.closest('[data-visor]');
    if (enlace) {
      var visor = document.getElementById(enlace.dataset.visor);
      if (!visor || !visor.showModal) return; // sin <dialog>: el enlace abre la imagen normal
      e.preventDefault();
      var img = visor.querySelector('img');
      img.src = enlace.href;
      img.alt = enlace.dataset.titulo || '';
      visor.querySelector('p').textContent = enlace.dataset.titulo || '';
      visor.showModal();
      return;
    }
    // Cerrar con el botón o haciendo clic fuera de la imagen (en el fondo).
    var dialogo = e.target.closest('dialog');
    if (dialogo && (e.target === dialogo || e.target.closest('[data-cerrar]'))) dialogo.close();
  });

  // ---------- Analíticas (solo con consentimiento) ----------
  // Las cookies de visita las pone el servidor (httpOnly); aquí solo se avisa qué pasó.
  function enviarEvento(tipo, segundos) {
    if (document.documentElement.dataset.consentimiento !== 'aceptado') return;
    var p = new URLSearchParams(location.search);
    var datos = JSON.stringify({
      tipo: tipo,
      ruta: location.pathname,
      segundos: segundos || 0,
      // De dónde llegó: el servidor guarda solo el dominio, y solo lo usa al iniciar la visita.
      referente: document.referrer || null,
      utm_source: p.get('utm_source'),
      utm_medium: p.get('utm_medium'),
      utm_campaign: p.get('utm_campaign'),
    });
    // sendBeacon sobrevive al cierre de la página; si no está o falla, fetch con keepalive.
    if (!(navigator.sendBeacon && navigator.sendBeacon('/api/eventos', datos))) {
      fetch('/api/eventos', { method: 'POST', body: datos, keepalive: true }).catch(function () {});
    }
  }
  enviarEvento('pageview');

  // Duración real de la visita: se mide solo el tiempo con la página visible y se envía cada 15 s.
  // Al ocultarse (cambio de pestaña, cerrar o navegar a otra página) se envía lo que quedó pendiente.
  var visibleDesde = document.visibilityState === 'visible' ? Date.now() : null;
  var pendienteMs = 0;
  function latir() {
    if (visibleDesde) { pendienteMs += Date.now() - visibleDesde; visibleDesde = Date.now(); }
    var segundos = Math.floor(pendienteMs / 1000);
    pendienteMs -= segundos * 1000; // el resto se suma al próximo latido
    if (segundos) enviarEvento('heartbeat', segundos);
  }
  function reiniciarDuracion() { pendienteMs = 0; visibleDesde = document.visibilityState === 'visible' ? Date.now() : null; }
  setInterval(function () { if (document.visibilityState === 'visible') latir(); }, 15000);
  document.addEventListener('visibilitychange', function () {
    if (document.visibilityState === 'hidden') { latir(); visibleDesde = null; } else { visibleDesde = Date.now(); }
  });

  // Galería: abrir una imagen y moverse con las flechas.
  document.addEventListener('click', function (e) {
    if (e.target.closest('[data-visor="visor-galeria"]')) enviarEvento('gallery_open');
    else if (e.target.closest('[data-mover][data-pista="pista-galeria"]')) enviarEvento('gallery_navigate');
  });

  // ---------- Banner de cookies ----------
  var banner = document.getElementById('banner-cookies');
  if (banner) {
    var token = document.querySelector('meta[name="csrf-token"]').content;
    var aviso = banner.querySelector('[data-error-cookies]');

    banner.addEventListener('click', function (e) {
      var boton = e.target.closest('[data-decision]');
      if (!boton) return;
      aviso.hidden = true;
      fetch('/api/consentimiento', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token },
        body: JSON.stringify({ decision: boton.dataset.decision }),
      }).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        banner.hidden = true;
        var antes = document.documentElement.dataset.consentimiento;
        document.documentElement.dataset.consentimiento = boton.dataset.decision;
        if (boton.dataset.decision === 'aceptado' && antes !== 'aceptado') {
          reiniciarDuracion(); // el tiempo antes de aceptar no se cuenta
          enviarEvento('pageview'); // cuenta la página actual
        }
      }).catch(function () { aviso.hidden = false; });
    });

    // "Preferencias de cookies" (footer y política): vuelve a mostrar el banner para cambiar la decisión.
    document.addEventListener('click', function (e) {
      if (!e.target.closest('[data-preferencias-cookies]')) return;
      banner.hidden = false;
      banner.querySelector('h2').focus();
    });
  }

  // ---------- Eliminar mis datos (página de privacidad) ----------
  document.addEventListener('click', function (e) {
    var boton = e.target.closest('[data-eliminar-mis-datos]');
    if (!boton) return;
    if (!confirm('¿Borrar los datos de tus visitas y retirar tu consentimiento? No se puede deshacer.')) return;
    var resultado = document.querySelector('[data-resultado-eliminar]');
    boton.disabled = true;
    fetch('/api/privacidad/eliminar-mis-datos', {
      method: 'POST',
      headers: { 'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content },
    }).then(function (r) {
      if (!r.ok) throw new Error(r.status);
      return r.json();
    }).then(function (datos) {
      document.documentElement.dataset.consentimiento = 'rechazado';
      resultado.textContent = datos.visitas_eliminadas
        ? 'Listo: borramos ' + datos.visitas_eliminadas + ' visita(s) y retiramos tu consentimiento.'
        : 'No había datos de visitas guardados desde este navegador. Tu consentimiento quedó retirado.';
    }).catch(function () {
      boton.disabled = false;
      resultado.textContent = 'No pudimos completar la solicitud. Inténtalo de nuevo.';
    });
  });

  // ---------- Mapa: se carga solo al pulsar (Google recibe la IP y pone sus cookies) ----------
  document.addEventListener('click', function (e) {
    var boton = e.target.closest('[data-cargar-mapa]');
    if (!boton) return;
    var mapa = document.getElementById(boton.dataset.cargarMapa);
    mapa.src = mapa.dataset.src;
    mapa.hidden = false;
    boton.parentElement.remove(); // quita el botón y su aviso
  });

  // ---------- Archivo del blog ----------
  var grupos = document.querySelectorAll('[data-mes]');
  var enlaces = document.querySelectorAll('[data-objetivo]');
  if (grupos.length && enlaces.length && 'IntersectionObserver' in window) {
    var observador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (entrada) {
        if (!entrada.isIntersecting) return;
        enlaces.forEach(function (a) {
          a.toggleAttribute('data-activo', a.dataset.objetivo === entrada.target.id);
        });
      });
    }, { rootMargin: '-15% 0px -70% 0px' });
    grupos.forEach(function (g) { observador.observe(g); });
  }
})();
