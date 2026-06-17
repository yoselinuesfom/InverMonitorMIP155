from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import PerfilUsuario  

@login_required(login_url='/login/')
def Perfil(request):
    usuario = request.user
    perfil, _ = PerfilUsuario.objects.get_or_create(
        usuario=usuario,
        defaults={'nombre': usuario.get_full_name() or usuario.username}
    )

    if request.method == 'POST':
        accion = request.POST.get('accion')

        #  Actualizar información personal 
        if accion == 'actualizar_perfil':
            nombre   = request.POST.get('nombre', '').strip()
            telefono = request.POST.get('telefono', '').strip()
            email    = request.POST.get('email', '').strip()

            # Actualizar perfil
            if nombre:
                perfil.nombre = nombre
                # Sincronizar con first_name / last_name de User
                partes = nombre.split(' ', 1)
                usuario.first_name = partes[0]
                usuario.last_name  = partes[1] if len(partes) > 1 else ''

            perfil.telefono = telefono
            perfil.save()

            # Actualizar email del usuario
            if email:
                usuario.email = email

            usuario.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('perfil')

        #  Cambiar contraseña 
        elif accion == 'cambiar_password':
            password_actual    = request.POST.get('password_actual', '')
            password_nuevo     = request.POST.get('password_nuevo', '')
            password_confirmar = request.POST.get('password_confirmar', '')

            if not usuario.check_password(password_actual):
                messages.error(request, 'La contraseña actual es incorrecta.')
            elif password_nuevo != password_confirmar:
                messages.error(request, 'Las contraseñas nuevas no coinciden.')
            elif len(password_nuevo) < 8:
                messages.error(request, 'La nueva contraseña debe tener al menos 8 caracteres.')
            else:
                usuario.set_password(password_nuevo)
                usuario.save()
                # Mantener la sesión activa después del cambio
                update_session_auth_hash(request, usuario)
                messages.success(request, 'Contraseña actualizada correctamente.')

            return redirect('perfil')

    contexto = {
        'perfil': perfil,
    }
    return render(request, 'perfil.html', contexto)