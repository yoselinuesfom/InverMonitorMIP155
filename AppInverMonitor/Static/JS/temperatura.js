/* ================================================================
   temperatura.js  —  InverMonitor
   - El reloj, sidebar y tema los maneja dashboard.js (ya cargado).
   - Este archivo solo agrega el auto-refresh de datos cada 30 s.
   ================================================================ */

document.addEventListener('DOMContentLoaded', () => {

    const INTERVALO_MS  = 30_000;   // 30 segundos
    const TOTAL_SEG     = 30;
    let segundos        = TOTAL_SEG;

    // ── Contador regresivo en topbar ──────────────────────────────
    const contadorEl = document.createElement('div');
    contadorEl.className  = 'reloj-topbar';
    contadorEl.title      = 'Clic para actualizar ahora';
    contadorEl.style.cursor = 'pointer';
    contadorEl.innerHTML  = `<i class="bi bi-arrow-clockwise"></i>&nbsp;<span id="cuentaRegresiva">${TOTAL_SEG}s</span>`;

    const topbarDerecha = document.querySelector('.topbar-derecha');
    const reloj = topbarDerecha?.querySelector('.reloj-topbar');
    if (reloj) reloj.before(contadorEl);

    // Tick del contador
    const tickInterval = setInterval(() => {
        if (document.hidden) return;
        segundos = segundos <= 1 ? TOTAL_SEG : segundos - 1;
        const span = document.getElementById('cuentaRegresiva');
        if (span) span.textContent = `${segundos}s`;
    }, 1_000);

    // ── Función principal de refresh ─────────────────────────────
    function refreshTemperatura() {
        fetch(window.location.href, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(r => r.ok ? r.json() : null)
        .catch(() => null)
        .then(data => {
            if (!data) return;
            aplicarDatos(data);
            segundos = TOTAL_SEG;   // reset contador
        });
    }

    // ── Aplica los datos recibidos al DOM ─────────────────────────
    function aplicarDatos(data) {

        // Temperatura numérica
        const elTemp = document.getElementById('tempActual');
        if (elTemp && data.temp_actual != null) {
            elTemp.innerHTML = `${data.temp_actual}<span class="valor-principal-unidad">°C</span>`;
            elTemp.classList.add('temp-actualizado');
            setTimeout(() => elTemp.classList.remove('temp-actualizado'), 700);
        }

        // Badge de estado
        const elEstado = document.getElementById('estadoActual');
        if (elEstado && data.estado_actual) {
            const mapa = {
                'Alta':   ['estado-badge-alta',   'bi-thermometer-high', 'Alta'],
                'Baja':   ['estado-badge-baja',   'bi-thermometer-snow', 'Baja'],
                'Normal': ['estado-badge-normal', 'bi-check-circle',     'Normal'],
            };
            const [cls, ico, lbl] = mapa[data.estado_actual] ?? mapa['Normal'];
            elEstado.className = `estado-actual-badge ${cls}`;
            elEstado.innerHTML = `<i class="bi ${ico}"></i> ${lbl}`;
        }

        // Fecha / hora última lectura
        const elFecha = document.getElementById('fechaLectura');
        if (elFecha && data.fecha_lectura) {
            elFecha.innerHTML = `<i class="bi bi-clock"></i> ${data.fecha_lectura}`;
        }

        // Icono y label de tendencia (sección 4)
        const elIcono = document.getElementById('tendenciaIcono');
        const elLabel = document.getElementById('tendenciaLabel');
        const elDesc  = document.getElementById('tendenciaDesc');

        if (elIcono && data.tendencia) {
            const tend = {
                'subiendo': {
                    cls: 'tend-color-sube',
                    ico: 'bi-graph-up-arrow',
                    lbl: 'Subiendo rápido',
                    desc: 'La temperatura aumentó más de 1 °C respecto al registro anterior.',
                },
                'bajando': {
                    cls: 'tend-color-baja',
                    ico: 'bi-graph-down-arrow',
                    lbl: 'Bajando rápido',
                    desc: 'La temperatura disminuyó más de 1 °C respecto al registro anterior.',
                },
                'estable': {
                    cls: 'tend-color-estable',
                    ico: 'bi-arrow-right',
                    lbl: 'Estable',
                    desc: 'La temperatura se mantiene dentro del mismo rango.',
                },
            };
            const t = tend[data.tendencia] ?? tend['estable'];

            elIcono.className = `tendencia-icono-wrap ${t.cls}`;
            elIcono.innerHTML = `<i class="bi ${t.ico}"></i>`;

            if (elLabel) {
                elLabel.className = `tendencia-label ${t.cls}`;
                elLabel.textContent = t.lbl;
            }
            if (elDesc) elDesc.textContent = t.desc;
        }
    }

    // ── Ciclo de auto-refresh ─────────────────────────────────────
    let timerRefresh = setInterval(refreshTemperatura, INTERVALO_MS);

    // Pausa al cambiar de pestaña
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            clearInterval(timerRefresh);
        } else {
            refreshTemperatura();
            timerRefresh = setInterval(refreshTemperatura, INTERVALO_MS);
        }
    });

    // Clic en contador = refresh inmediato
    contadorEl.addEventListener('click', () => {
        clearInterval(timerRefresh);
        refreshTemperatura();
        timerRefresh = setInterval(refreshTemperatura, INTERVALO_MS);
    });

});

/* ================================================================
   AJUSTE NECESARIO EN views.py — función Temperatura()

   Agrega esto ANTES del return render(...) final:

   if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
       from django.http import JsonResponse
       return JsonResponse({
           'temp_actual':       contexto['temp_actual'],
           'estado_actual':     contexto['estado_actual'],
           'fecha_lectura':     contexto['fecha_lectura'],
           'tendencia':         contexto['tendencia'],
           'altura_termometro': contexto['altura_termometro'],
       })

   Las peticiones normales de navegador siguen devolviendo render().
   ================================================================ */