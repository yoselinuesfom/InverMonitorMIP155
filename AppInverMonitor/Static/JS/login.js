// ══════════════════════════════════════════
//  Toggle mostrar / ocultar contraseña
//  La validación la maneja Django en el servidor
// ══════════════════════════════════════════
const togglePassword = document.getElementById('togglePassword');
const passwordInput  = document.getElementById('password');
const toggleIcon     = document.getElementById('toggleIcon');

if (togglePassword) {
    togglePassword.addEventListener('click', () => {
        const isHidden = passwordInput.type === 'password';
        passwordInput.type   = isHidden ? 'text' : 'password';
        toggleIcon.className = isHidden ? 'bi bi-eye-slash' : 'bi bi-eye';
    });
}

// ══════════════════════════════════════════
//  Feedback visual al hacer submit
//  (solo UI — Django procesa el form)
// ══════════════════════════════════════════
const loginForm = document.querySelector('form');
const btnLogin  = document.querySelector('.btn-login');

if (loginForm && btnLogin) {
    loginForm.addEventListener('submit', () => {
        btnLogin.disabled = true;
        btnLogin.innerHTML = `
            <i class="bi bi-arrow-repeat spin"></i>
            <span>Ingresando...</span>
        `;
    });
}

// ══════════════════════════════════════════
//  Spinner CSS (inyectado por JS para no
//  depender de una clase extra en el CSS)
// ══════════════════════════════════════════
const style = document.createElement('style');
style.textContent = `
    .spin {
        display: inline-block;
        animation: spin 0.7s linear infinite;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);