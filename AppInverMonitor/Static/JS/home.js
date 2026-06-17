document.addEventListener('DOMContentLoaded', () => {

    //  MÉTRICAS EN VIVO 
    function actualizarMetricas() {
        const temp = (22 + Math.random() * 6).toFixed(1);
        const hum  = Math.round(65 + Math.random() * 25);
        const lum  = (2.5 + Math.random() * 4).toFixed(1);

        document.getElementById('valorTemp').textContent = temp + '°C';
        document.getElementById('valorHum').textContent  = hum + '%';
        document.getElementById('valorLum').textContent  = lum + ' klx';

        document.getElementById('barraTemp').style.width = ((parseFloat(temp) - 10) / 30 * 100) + '%';
        document.getElementById('barraHum').style.width  = hum + '%';
        document.getElementById('barraLum').style.width  = (parseFloat(lum) / 10 * 100) + '%';
    }
    setInterval(actualizarMetricas, 2500);

    //  CONTADOR ANIMADO 
    function animarContador(elemento, objetivo, sufijo) {
        let actual = 0;
        const incremento = objetivo / 60;
        const intervalo = setInterval(() => {
            actual += incremento;
            if (actual >= objetivo) { actual = objetivo; clearInterval(intervalo); }
            elemento.textContent = Math.round(actual) + (sufijo || '');
        }, 25);
    }

    const observadorEstadisticas = new IntersectionObserver((entradas) => {
        entradas.forEach(entrada => {
            if (entrada.isIntersecting) {
                entrada.target.querySelectorAll('[data-objetivo]').forEach(num => {
                    animarContador(num, parseInt(num.dataset.objetivo), num.dataset.sufijo || '');
                });
                observadorEstadisticas.unobserve(entrada.target);
            }
        });
    }, { threshold: 0.3 });

    const seccionEstadisticas = document.querySelector('.seccion-estadisticas');
    if (seccionEstadisticas) observadorEstadisticas.observe(seccionEstadisticas);

    //  ANIMACIONES DE ENTRADA 
    const observadorEntrada = new IntersectionObserver((entradas) => {
        entradas.forEach((entrada, indice) => {
            if (entrada.isIntersecting) {
                setTimeout(() => entrada.target.classList.add('visible'), indice * 80);
                observadorEntrada.unobserve(entrada.target);
            }
        });
    }, { threshold: 0.1 });

    document.querySelectorAll('.animar-entrada').forEach(el => observadorEntrada.observe(el));

    //  NAVBAR AL SCROLL 
    window.addEventListener('scroll', () => {
        const navBarra = document.querySelector('.nav-barra');
        if (navBarra) {
            navBarra.style.borderBottomColor = window.scrollY > 50
                ? 'rgba(46, 204, 113, 0.25)'
                : 'rgba(46, 204, 113, 0.15)';
        }
    });

}); 