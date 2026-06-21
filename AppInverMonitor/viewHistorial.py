
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def Historial(request):
    registros = request.user.registros.all()
    config = getattr(request.user, 'config_alarma', None)
    return render(request, 'historial.html', {
        'registros': registros,
        'config': config
    })