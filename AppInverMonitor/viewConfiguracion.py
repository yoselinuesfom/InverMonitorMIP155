from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ConfiguracionAlarma
from .formConfiguracion import ConfiguracionAlarmaForm  # Importa tu nuevo formulario

@login_required(login_url='login')
def Configuracion(request):
    config_instancia = request.user.config_alarma
    if request.method == 'POST':
        form = ConfiguracionAlarmaForm(request.POST, instance=config_instancia)  
        if form.is_valid():
            form.save()
            messages.success(request, "¡Configuración de alertas actualizada correctamente!")
            return redirect(request.META.get('HTTP_REFERER', 'configuracion_guardar'))
        else:
            messages.error(request, "Hubo un error al validar los datos. Revisa los valores ingresados.")
    else:
        form = ConfiguracionAlarmaForm(instance=config_instancia)
    return render(request, 'configuracion.html', {
        'form': form, 
        'config': config_instancia
    })