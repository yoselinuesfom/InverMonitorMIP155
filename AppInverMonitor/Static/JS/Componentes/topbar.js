
//  Reloj en tiempo real 
(function () {
    function actualizarReloj() {
        const ahora = new Date();

        const h = String(ahora.getHours()).padStart(2, '0');
        const m = String(ahora.getMinutes()).padStart(2, '0');
        const s = String(ahora.getSeconds()).padStart(2, '0');

        const clock = document.getElementById('clockDisplay');
        if (clock) clock.textContent = `${h}:${m}:${s}`;

        const dias  = ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'];
        const meses = ['enero','febrero','marzo','abril','mayo','junio','julio',
                       'agosto','septiembre','octubre','noviembre','diciembre'];
        const fechaStr = `${dias[ahora.getDay()]}, ${ahora.getDate()} de ${meses[ahora.getMonth()]} de ${ahora.getFullYear()}`;

        const fecha = document.getElementById('currentDate');
        if (fecha) fecha.textContent = fechaStr;
    }

    actualizarReloj();
    setInterval(actualizarReloj, 1000);
})();

// ── Toggle tema oscuro / claro ──
(function () {
    const botonTema  = document.getElementById('botonTema');
    const temaGuardado = localStorage.getItem('tema') || 'oscuro';

    function aplicarTema(tema) {
        document.documentElement.setAttribute('data-tema', tema === 'claro' ? 'claro' : '');
        if (botonTema) botonTema.textContent = tema === 'claro' ? '🌙' : '☀️';
        localStorage.setItem('tema', tema);
    }

    aplicarTema(temaGuardado);

    if (botonTema) {
        botonTema.addEventListener('click', function () {
            const temaActual = localStorage.getItem('tema') || 'oscuro';
            aplicarTema(temaActual === 'oscuro' ? 'claro' : 'oscuro');
        });
    }
})();