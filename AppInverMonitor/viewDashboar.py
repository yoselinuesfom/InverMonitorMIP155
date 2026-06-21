from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Max, Min, Avg
from .models import RegistroSensor

@login_required(login_url='login')
def Dashboard(request):
    usuario = request.user
    hoy = timezone.now().date()
    hace_12h = timezone.now() - timedelta(hours=12)

    # Ultimo registro
    ultimo = RegistroSensor.objects.filter(usuario=usuario).first()

    # estadistica del dia de hoy
    registros_hoy = RegistroSensor.objects.filter(
        usuario=usuario,
        fecha_hora__date=hoy
    )
    stats_hoy = registros_hoy.aggregate(
        temp_max=Max('temperatura'),
        temp_min=Min('temperatura'),
        temp_avg=Avg('temperatura'),
        hum_max=Max('humedad'),
        hum_min=Min('humedad'),
        hum_avg=Avg('humedad'),
        lux_max=Max('luminosidad'),
        lux_min=Min('luminosidad'),
        lux_avg=Avg('luminosidad'),
        suelo_max=Max('humedad_suelo'),
        suelo_min=Min('humedad_suelo'),
        suelo_avg=Avg('humedad_suelo'),
    )

    # Ultimas 10 lecturas para la tabla
    ultimas_lecturas = RegistroSensor.objects.filter(
        usuario=usuario
    )[:10]

    # Datos para gráficas ultimas 12 horas Max 50 puntos
    registros_grafica = RegistroSensor.objects.filter(
        usuario=usuario,
        fecha_hora__gte=hace_12h
    ).order_by('fecha_hora')[:50]

    labels      = [r.fecha_hora.strftime('%H:%M') for r in registros_grafica]
    data_temp   = [r.temperatura     for r in registros_grafica]
    data_hum    = [r.humedad         for r in registros_grafica]
    data_lux    = [r.luminosidad     for r in registros_grafica]
    data_suelo  = [r.humedad_suelo   for r in registros_grafica]

    # Tendencia: comparar último registro con el anterior
    registros_recientes = RegistroSensor.objects.filter(usuario=usuario)[:2]
    tendencias = {'temp': 0, 'hum': 0, 'lux': 0, 'suelo': 0}
    if len(registros_recientes) == 2:
        actual, anterior = registros_recientes[0], registros_recientes[1]
        tendencias['temp']  = round(actual.temperatura   - anterior.temperatura,   1)
        tendencias['hum']   = round(actual.humedad       - anterior.humedad,       1)
        tendencias['lux']   = round(actual.luminosidad   - anterior.luminosidad,   0)
        tendencias['suelo'] = round(actual.humedad_suelo - anterior.humedad_suelo, 1)

    # Total lecturas hoy
    total_lecturas_hoy = registros_hoy.count()

    context = {
        'ultimo':             ultimo,
        'stats_hoy':          stats_hoy,
        'ultimas_lecturas':   ultimas_lecturas,
        'labels':             labels,
        'data_temp':          data_temp,
        'data_hum':           data_hum,
        'data_lux':           data_lux,
        'data_suelo':         data_suelo,
        'tendencias':         tendencias,
        'total_lecturas_hoy': total_lecturas_hoy,
    }
    return render(request, 'dashboard.html', context)