// ══════════════════════════════════════════
//  SIDEBAR.JS — Toggle móvil
//  invermonitor/js/sidebar.js
// ══════════════════════════════════════════

(function () {
    const sidebar      = document.getElementById('sidebar');
    const botonSidebar = document.getElementById('sidebarToggle');

    if (!sidebar || !botonSidebar) return;

    botonSidebar.addEventListener('click', function () {
        sidebar.classList.toggle('abierto');
    });

    document.addEventListener('click', function (e) {
        if (
            window.innerWidth <= 768 &&
            !sidebar.contains(e.target) &&
            !botonSidebar.contains(e.target)
        ) {
            sidebar.classList.remove('abierto');
        }
    });
})();