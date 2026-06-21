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

//  TOGGLE SIDEBAR (móvil)
const sidebar      = document.getElementById('sidebar');
const botonSidebar = document.getElementById('sidebarToggle');

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


//  COLORES DE GRÁFICAS SEGÚN TEMA
function esClaro() {
    return document.documentElement.getAttribute('data-tema') === 'claro';
}

function getColoresGrafica() {
    const claro = esClaro();
    return {
        tickColor:    claro ? '#1e5c38' : '#3d6e4f',
        gridColor:    claro ? '#c5e0ce' : '#162a1c',
        tooltipBg:    claro ? '#ffffff' : '#0d1f12',
        tooltipBorde: claro ? '#1a7a4a' : '#1a7a4a',
        tooltipTitulo:claro ? '#0a1f11' : '#7aab8a',
        tooltipCuerpo:claro ? '#1e5c38' : '#e8f5ec',
    };
}

//  CONFIGURACIÓN BASE DE GRÁFICAS
const etiquetasHoras = ['23:00','00:00','01:00','02:00','03:00','04:00',
                        '05:00','06:00','07:00','08:00','09:00','10:00','11:00'];

const baseDataset = {
    borderWidth:      1.5,
    pointRadius:      0,
    pointHoverRadius: 4,
    tension:          0.4,
    fill:             true,
};

function crearGradiente(ctx, colorBase) {
    const gradiente = ctx.createLinearGradient(0, 0, 0, 180);
    gradiente.addColorStop(0, colorBase);
    gradiente.addColorStop(1, 'rgba(0,0,0,0)');
    return gradiente;
}

// Gradiente adaptado al fondo claro (usa blanco en vez de negro transparente)
function crearGradienteClaro(ctx, colorBase) {
    const gradiente = ctx.createLinearGradient(0, 0, 0, 180);
    gradiente.addColorStop(0, colorBase);
    gradiente.addColorStop(1, 'rgba(255,255,255,0)');
    return gradiente;
}

function crearOpcionesBase() {
    const c = getColoresGrafica();
    return {
        responsive:          true,
        maintainAspectRatio: true,
        interaction: { mode: 'index', intersect: false },
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: c.tooltipBg,
                borderColor:     c.tooltipBorde,
                borderWidth:     1,
                titleColor:      c.tooltipTitulo,
                bodyColor:       c.tooltipCuerpo,
                padding:         10,
                cornerRadius:    7,
            },
        },
        scales: {
            x: {
                grid:  { color: c.gridColor, drawBorder: false },
                ticks: { color: c.tickColor, font: { size: 10 } },
            },
            y: {
                grid:  { color: c.gridColor, drawBorder: false },
                ticks: { color: c.tickColor, font: { size: 10 } },
            },
        },
    };
}

//  REGISTRO DE INSTANCIAS DE GRÁFICAS
const instanciasGraficas = {};

function crearGrafica(id, label, datos, colorBorde, colorFondoOscuro, colorFondoClaro) {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    const claro = esClaro();
    const bgGrad = claro
        ? crearGradienteClaro(ctx, colorFondoClaro)
        : crearGradiente(ctx, colorFondoOscuro);

    if (instanciasGraficas[id]) {
        instanciasGraficas[id].destroy();
    }

    instanciasGraficas[id] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: etiquetasHoras,
            datasets: [{
                ...baseDataset,
                label:           label,
                data:            datos,
                borderColor:     colorBorde,
                backgroundColor: bgGrad,
            }]
        },
        options: crearOpcionesBase(),
    });
}

function renderizarTodasLasGraficas() {
    crearGrafica(
        'chartTemp',
        'Temperatura (°C)',
        [21.2,20.8,20.3,19.8,19.1,19.5,20.4,21.6,22.9,23.8,24.1,24.6,24.6],
        '#fc8181',
        'rgba(252,129,129,0.18)',
        'rgba(220,38,38,0.12)'
    );
    crearGrafica(
        'chartHum',
        'Humedad (%)',
        [78,80,82,81,80,79,76,74,73,71,70,68,67],
        '#3daaf0',
        'rgba(61,170,240,0.18)',
        'rgba(37,99,235,0.12)'
    );
    crearGrafica(
        'chartLux',
        'Luminosidad (lux)',
        [0,0,0,0,0,0,210,480,620,720,760,812,830],
        '#f0a500',
        'rgba(240,165,0,0.15)',
        'rgba(217,119,6,0.12)'
    );
}

// Renderizar al cargar
renderizarTodasLasGraficas();

//  TOGGLE TEMA OSCURO / CLARO
const botonTema    = document.getElementById('botonTema');
const temaGuardado = localStorage.getItem('tema') || 'oscuro';

function aplicarTema(tema) {
    document.documentElement.setAttribute('data-tema', tema === 'claro' ? 'claro' : '');

    if (botonTema) {
        const icono = botonTema.querySelector('i');
        if (icono) {
            icono.className = tema === 'claro' ? 'bi bi-moon-stars-fill' : 'bi bi-brightness-high-fill';
        } else {
            botonTema.innerHTML = tema === 'claro'
                ? '<i class="bi bi-moon-stars-fill"></i>'
                : '<i class="bi bi-brightness-high-fill"></i>';
        }
    }

    localStorage.setItem('tema', tema);

    // Re-renderizar gráficas con los nuevos colores
    renderizarTodasLasGraficas();
}

aplicarTema(temaGuardado);

botonTema?.addEventListener('click', () => {
    const temaActual = localStorage.getItem('tema') || 'oscuro';
    aplicarTema(temaActual === 'oscuro' ? 'claro' : 'oscuro');
});