from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from .models import NotificacionAlerta


@login_required(login_url='login')
def Notificaciones(request):
    usuario = request.user

    # Filtros opcionales por sensor y tipo
    sensor_filtro = request.GET.get('sensor', '')
    tipo_filtro   = request.GET.get('tipo', '')

    notificaciones = NotificacionAlerta.objects.filter(usuario=usuario)

    if sensor_filtro:
        notificaciones = notificaciones.filter(sensor=sensor_filtro)
    if tipo_filtro:
        notificaciones = notificaciones.filter(tipo=tipo_filtro)

    # Marcar todas como leídas al entrar
    notificaciones.filter(leida=False).update(leida=True)

    # Paginación — 15 por página
    paginator = Paginator(notificaciones, 15)
    page      = request.GET.get('page', 1)
    page_obj  = paginator.get_page(page)

    # Conteos para las tarjetas resumen
    total        = NotificacionAlerta.objects.filter(usuario=usuario).count()
    criticas_alta = NotificacionAlerta.objects.filter(usuario=usuario, tipo='alta').count()
    criticas_baja = NotificacionAlerta.objects.filter(usuario=usuario, tipo='baja').count()

    context = {
        'page_obj':      page_obj,
        'sensor_filtro': sensor_filtro,
        'tipo_filtro':   tipo_filtro,
        'total':         total,
        'criticas_alta': criticas_alta,
        'criticas_baja': criticas_baja,
        'sensores': [
            ('temperatura',   'Temperatura'),
            ('humedad',       'Humedad'),
            ('luminosidad',   'Luminosidad'),
            ('humedad_suelo', 'Humedad Suelo'),
        ],
    }
    return render(request, 'notificaciones.html', context)