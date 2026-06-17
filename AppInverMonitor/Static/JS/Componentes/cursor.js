 // Cursor personalizado
  const cursorPunto = document.getElementById('cursorPunto');
  const cursorSeguidor = document.getElementById('cursorSeguidor');
  const brilloFondo = document.getElementById('brilloFondo');

  let ratXActual = 0, ratYActual = 0;
  let ratXSeguidor = 0, ratYSeguidor = 0;

  document.addEventListener('mousemove', (e) => {
    ratXActual = e.clientX;
    ratYActual = e.clientY;
    cursorPunto.style.left = ratXActual - 6 + 'px';
    cursorPunto.style.top = ratYActual - 6 + 'px';
    brilloFondo.style.left = ratXActual - 300 + 'px';
    brilloFondo.style.top = ratYActual - 300 + 'px';
  });

  function animarSeguidor() {
    ratXSeguidor += (ratXActual - ratXSeguidor) * 0.12;
    ratYSeguidor += (ratYActual - ratYSeguidor) * 0.12;
    cursorSeguidor.style.left = ratXSeguidor - 18 + 'px';
    cursorSeguidor.style.top = ratYSeguidor - 18 + 'px';
    requestAnimationFrame(animarSeguidor);
  }
  animarSeguidor();