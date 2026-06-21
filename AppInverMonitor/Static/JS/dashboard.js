function actualizarReloj() {
    const ahora = new Date();

    const h = String(ahora.getHours()).padStart(2, '0');
    const m = String(ahora.getMinutes()).padStart(2, '0');
    const s = String(ahora.getSeconds()).padStart(2, '0');
    document.getElementById('clockDisplay').textContent = `${h}:${m}:${s}`;

    const dias   = ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'];
    const meses  = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
    const fechaStr = `${dias[ahora.getDay()]}, ${ahora.getDate()} de ${meses[ahora.getMonth()]} de ${ahora.getFullYear()}`;
    document.getElementById('currentDate').textContent = fechaStr;
}

actualizarReloj();
setInterval(actualizarReloj, 1000);

// ══════════════════════════════════════════
//  TOGGLE SIDEBAR (móvil)
// ══════════════════════════════════════════
const sidebar        = document.getElementById('sidebar');
const botonSidebar   = document.getElementById('sidebarToggle');

botonSidebar?.addEventListener('click', () => {
    sidebar.classList.toggle('abierto');
});

document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768 &&
        !sidebar.contains(e.target) &&
        !botonSidebar.contains(e.target)) {
        sidebar.classList.remove('abierto');
    }
});

// ══════════════════════════════════════════
//  TOGGLE TEMA OSCURO / CLARO
// ══════════════════════════════════════════
const botonTema = document.getElementById('botonTema');
const temaGuardado = localStorage.getItem('tema') || 'oscuro';

function aplicarTema(tema) {
    document.documentElement.setAttribute('data-tema', tema === 'claro' ? 'claro' : '');
    if (botonTema) {
        const icono = botonTema.querySelector('i');
        if (icono) {
            icono.className = tema === 'claro' ? 'bi bi-moon-stars-fill' : 'bi bi-brightness-high-fill';
        } else {
            // Si el botón no tiene <i> adentro (como en el topbar.html duplicado), lo crea
            botonTema.innerHTML = tema === 'claro'
                ? '<i class="bi bi-moon-stars-fill"></i>'
                : '<i class="bi bi-brightness-high-fill"></i>';
        }
    }
    localStorage.setItem('tema', tema);
}

aplicarTema(temaGuardado);

botonTema?.addEventListener('click', () => {
    const temaActual = localStorage.getItem('tema') || 'oscuro';
    aplicarTema(temaActual === 'oscuro' ? 'claro' : 'oscuro');
});

// ══════════════════════════════════════════
//  CONFIGURACIÓN BASE DE GRÁFICAS
// ══════════════════════════════════════════
const etiquetasHoras = ['23:00','00:00','01:00','02:00','03:00','04:00',
                        '05:00','06:00','07:00','08:00','09:00','10:00','11:00'];

const baseDataset = {
    borderWidth:       1.5,
    pointRadius:       0,
    pointHoverRadius:  4,
    tension:           0.4,
    fill:              true,
};

function crearGradiente(ctx, colorBase) {
    const gradiente = ctx.createLinearGradient(0, 0, 0, 180);
    gradiente.addColorStop(0, colorBase);
    gradiente.addColorStop(1, 'rgba(0,0,0,0)');
    return gradiente;
}

const opcionesBase = {
    responsive:          true,
    maintainAspectRatio: true,
    interaction: { mode: 'index', intersect: false },
    plugins: {
        legend: { display: false },
        tooltip: {
            backgroundColor: '#0d1f12',
            borderColor:     '#1a7a4a',
            borderWidth:     1,
            titleColor:      '#7aab8a',
            bodyColor:       '#e8f5ec',
            padding:         10,
            cornerRadius:    7,
        },
    },
    scales: {
        x: {
            grid:  { color: '#162a1c', drawBorder: false },
            ticks: { color: '#3d6e4f', font: { size: 10 } },
        },
        y: {
            grid:  { color: '#162a1c', drawBorder: false },
            ticks: { color: '#3d6e4f', font: { size: 10 } },
        },
    },
};

// ── Temperatura ──
(function() {
    const ctx = document.getElementById('chartTemp').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: etiquetasHoras,
            datasets: [{
                ...baseDataset,
                label:           'Temperatura (°C)',
                data:            [21.2,20.8,20.3,19.8,19.1,19.5,20.4,21.6,22.9,23.8,24.1,24.6,24.6],
                borderColor:     '#fc8181',
                backgroundColor: crearGradiente(ctx, 'rgba(252,129,129,0.18)'),
            }]
        },
        options: opcionesBase,
    });
})();

// ── Humedad ──
(function() {
    const ctx = document.getElementById('chartHum').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: etiquetasHoras,
            datasets: [{
                ...baseDataset,
                label:           'Humedad (%)',
                data:            [78,80,82,81,80,79,76,74,73,71,70,68,67],
                borderColor:     '#3daaf0',
                backgroundColor: crearGradiente(ctx, 'rgba(61,170,240,0.18)'),
            }]
        },
        options: opcionesBase,
    });
})();

// ── Luminosidad ──
(function() {
    const ctx = document.getElementById('chartLux').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: etiquetasHoras,
            datasets: [{
                ...baseDataset,
                label:           'Luminosidad (lux)',
                data:            [0,0,0,0,0,0,210,480,620,720,760,812,830],
                borderColor:     '#f0a500',
                backgroundColor: crearGradiente(ctx, 'rgba(240,165,0,0.15)'),
            }]
        },
        options: opcionesBase,
    });
})();