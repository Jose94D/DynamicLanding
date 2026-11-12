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
