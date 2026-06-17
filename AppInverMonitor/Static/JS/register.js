// ─── CURSOR PERSONALIZADO ───────────────────────────────────────────
const cursorPunto    = document.getElementById('cursorPunto');
const cursorSeguidor = document.getElementById('cursorSeguidor');
const brilloFondo    = document.getElementById('brilloFondo');

let ratXActual = 0, ratYActual = 0;
let ratXSeguidor = 0, ratYSeguidor = 0;

document.addEventListener('mousemove', (e) => {
    ratXActual = e.clientX;
    ratYActual = e.clientY;
    cursorPunto.style.left = ratXActual - 6 + 'px';
    cursorPunto.style.top  = ratYActual - 6 + 'px';
    brilloFondo.style.left = ratXActual - 300 + 'px';
    brilloFondo.style.top  = ratYActual - 300 + 'px';
});

function animarSeguidor() {
    ratXSeguidor += (ratXActual - ratXSeguidor) * 0.12;
    ratYSeguidor += (ratYActual - ratYSeguidor) * 0.12;
    cursorSeguidor.style.left = ratXSeguidor - 18 + 'px';
    cursorSeguidor.style.top  = ratYSeguidor - 18 + 'px';
    requestAnimationFrame(animarSeguidor);
}
animarSeguidor();

// ─── TOGGLE MOSTRAR / OCULTAR CONTRASEÑA ───────────────────────────
document.querySelectorAll('.btn-toggle-pass').forEach(btn => {
    btn.addEventListener('click', () => {
        const input = btn.previousElementSibling;
        const esPassword = input.type === 'password';
        input.type = esPassword ? 'text' : 'password';
        btn.textContent = esPassword ? '🙈' : '👁️';
    });
});

// ─── FORTALEZA DE CONTRASEÑA ────────────────────────────────────────
const inputPass = document.getElementById('password');
const barras    = document.querySelectorAll('.fortaleza-barra');
const textoFortaleza = document.getElementById('textoFortaleza');

function evaluarFortaleza(pass) {
    let puntaje = 0;
    if (pass.length >= 8)               puntaje++;
    if (/[A-Z]/.test(pass))             puntaje++;
    if (/[0-9]/.test(pass))             puntaje++;
    if (/[^A-Za-z0-9]/.test(pass))      puntaje++;
    return puntaje;
}

if (inputPass) {
    inputPass.addEventListener('input', () => {
        const pass    = inputPass.value;
        const puntaje = evaluarFortaleza(pass);

        barras.forEach((b, i) => {
            b.classList.remove('activa-debil', 'activa-media', 'activa-fuerte');
        });

        if (pass.length === 0) {
            textoFortaleza.textContent = '';
            return;
        }

        const claseActiva = puntaje <= 1 ? 'activa-debil' : puntaje <= 2 ? 'activa-media' : 'activa-fuerte';
        const labels      = ['', 'Débil', 'Regular', 'Buena', 'Fuerte'];

        for (let i = 0; i < puntaje; i++) {
            barras[i].classList.add(claseActiva);
        }
        textoFortaleza.textContent = labels[puntaje] || '';
    });
}

// ─── VALIDACIÓN DEL FORMULARIO ──────────────────────────────────────
const form = document.getElementById('registerForm');

function mostrarError(inputId, mensaje) {
    const input = document.getElementById(inputId);
    const msg   = document.getElementById('error-' + inputId);
    if (input) input.classList.add('error');
    if (msg)   { msg.textContent = mensaje; msg.classList.add('visible'); }
}

function limpiarError(inputId) {
    const input = document.getElementById(inputId);
    const msg   = document.getElementById('error-' + inputId);
    if (input) input.classList.remove('error');
    if (msg)   msg.classList.remove('visible');
}

// Limpiar error al escribir
['nombre', 'apellido', 'email', 'password', 'confirmar'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener('input', () => limpiarError(id));
});

if (form) {
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        let valido = true;

        const nombre    = document.getElementById('nombre')?.value.trim();
        const apellido  = document.getElementById('apellido')?.value.trim();
        const email     = document.getElementById('email')?.value.trim();
        const password  = document.getElementById('password')?.value;
        const confirmar = document.getElementById('confirmar')?.value;
        const terminos  = document.getElementById('terminos')?.checked;

        if (!nombre) {
            mostrarError('nombre', 'El nombre es requerido');
            valido = false;
        }
        if (!apellido) {
            mostrarError('apellido', 'El apellido es requerido');
            valido = false;
        }
        if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
            mostrarError('email', 'Ingresa un correo válido');
            valido = false;
        }
        if (!password || password.length < 8) {
            mostrarError('password', 'Mínimo 8 caracteres');
            valido = false;
        }
        if (password !== confirmar) {
            mostrarError('confirmar', 'Las contraseñas no coinciden');
            valido = false;
        }
        if (!terminos) {
            valido = false;
            // puedes mostrar un toast aquí si quieres
        }

        if (valido) {
            const btn = form.querySelector('.btn-register');
            btn.disabled    = true;
            btn.textContent = 'Creando cuenta...';
            // Aquí va el submit real (fetch/axios al backend Django)
            form.submit();
        }
    });
}

// Ocultar alertas después de 4 segundos
  setTimeout(() => {
    document.querySelectorAll('.alertas-flotantes .alert').forEach(alert => {
      alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(() => alert.remove(), 500);
    });
  }, 4000);


  