// ══════════════════════════════════════════
//  LAYOUT.JS — Carga dinámica de módulos
//  invermonitor/js/layout.js
// ══════════════════════════════════════════

(function () {
    const contenido = document.getElementById('contenidoDinamico');

    // Mapa de módulos: data-modulo → URL a cargar
    const MODULOS = {
        dashboard:      '/dashboard/',
        temperatura:    '/temperatura/',
        humedad:        '/humedad/',
        luminosidad:    '/luminosidad/',
        estadisticas:   '/estadisticas/',
        historial:      '/historial/',
        alertas:        '/alertas/',
        perfil:         '/perfil/',
        configuracion:  '/configuracion/',
        documentacion:  '/documentacion/',
        desarrolladores:'/desarrolladores/',
    };

    // Marca el item activo en el sidebar
    function marcarActivo(moduloId) {
        document.querySelectorAll('.item-nav').forEach(el => {
            el.classList.remove('activo');
            if (el.dataset.modulo === moduloId) {
                el.classList.add('activo');
            }
        });
    }

    // Carga el HTML del módulo vía fetch y lo inyecta en #contenidoDinamico
    function cargarModulo(moduloId) {
        const url = MODULOS[moduloId];
        if (!url || !contenido) return;

        marcarActivo(moduloId);

        fetch(url, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => {
            if (!res.ok) throw new Error('Error cargando módulo');
            return res.text();
        })
        .then(html => {
            contenido.innerHTML = html;
            // Ejecutar scripts inline que vengan en el fragmento
            contenido.querySelectorAll('script').forEach(oldScript => {
                const newScript = document.createElement('script');
                if (oldScript.src) {
                    newScript.src = oldScript.src;
                } else {
                    newScript.textContent = oldScript.textContent;
                }
                document.body.appendChild(newScript);
                oldScript.remove();
            });
            // Actualizar URL sin recargar
            history.pushState({ modulo: moduloId }, '', url);
        })
        .catch(err => {
            console.error('layout.js:', err);
        });
    }

    // Delegar clicks en todos los .item-nav con data-modulo
    document.addEventListener('click', function (e) {
        const item = e.target.closest('.item-nav[data-modulo]');
        if (!item) return;
        e.preventDefault();
        cargarModulo(item.dataset.modulo);
    });

    // Manejar botón atrás/adelante del navegador
    window.addEventListener('popstate', function (e) {
        if (e.state && e.state.modulo) {
            cargarModulo(e.state.modulo);
        }
    });

})();