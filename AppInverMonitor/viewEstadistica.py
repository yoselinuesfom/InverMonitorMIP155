import base64
from io import BytesIO
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Min, Count
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np
from .models import RegistroSensor, ConfiguracionAlarma

COLOR_FONDO       = '#111f15'
COLOR_FONDO_GRID  = '#162a1c'
COLOR_TEXTO       = '#7aab8a'
COLOR_TEXTO_TENUE = '#3d6e4f'
COLOR_TEMP        = '#fc8181'
COLOR_HUM         = '#3daaf0'
COLOR_LUX         = '#f0a500'

RANGOS_DIAS = {'7d': 7, '30d': 30, '90d': 90}

@login_required
def Estadistica(request):
    rango_activo = request.GET.get('rango', '7d')
    dias = RANGOS_DIAS.get(rango_activo, 7)

    usuario = request.user
    desde = timezone.now() - timedelta(days=dias)

    registros_periodo = RegistroSensor.objects.filter(
        usuario=usuario,
        fecha_hora__gte=desde,
    )
    todos_los_registros = RegistroSensor.objects.filter(usuario=usuario)

    # 1) KPIs
    kpi = obtener_kpis(usuario, todos_los_registros, registros_periodo, dias)

    # 2) Datos para la gráfica comparativa prom diario
    etiquetas, temp_data, hum_data, lux_data = obtener_datos_comparativos(registros_periodo, desde, dias)

    grafica_comparativa = None
    if etiquetas:
        grafica_comparativa = generar_grafica_comparativa(
            etiquetas, temp_data, hum_data, lux_data
        )

    # 3) Conteo de alertas analidi de segisntro segun umbrales del usuario
    alertas_resumen, alertas_total, riesgo_global = obtener_resumen_alertas(usuario, registros_periodo)

    contexto = {
        'kpi': kpi,
        'rango_activo': rango_activo,
        'grafica_comparativa': grafica_comparativa,
        'alertas_resumen': alertas_resumen,
        'alertas_total': alertas_total,
        'riesgo_global': riesgo_global,
    }
    return render(request, 'estadistica.html', contexto)



# 4) KPIs históricos
def obtener_kpis(usuario, todos_los_registros, registros_periodo, dias):
    # Máximos / mínimos históricos (de TODA la data del usuario)
    temp_max_reg = todos_los_registros.order_by('-temperatura').first()
    temp_min_reg = todos_los_registros.order_by('temperatura').first()

    # Promedios del periodo seleccionado
    promedios = registros_periodo.aggregate(
        hum_avg=Avg('humedad'),
        lux_avg=Avg('luminosidad'),
    )

    primer_registro = todos_los_registros.order_by('fecha_hora').first()

    return {
        'temp_max': round(temp_max_reg.temperatura, 1) if temp_max_reg else '—',
        'temp_max_fecha': formatear_fecha(temp_max_reg.fecha_hora) if temp_max_reg else '—',
        'temp_min': round(temp_min_reg.temperatura, 1) if temp_min_reg else '—',
        'temp_min_fecha': formatear_fecha(temp_min_reg.fecha_hora) if temp_min_reg else '—',
        'hum_promedio': round(promedios['hum_avg'], 0) if promedios['hum_avg'] is not None else '—',
        'lux_promedio': round(promedios['lux_avg'], 0) if promedios['lux_avg'] is not None else '—',
        'periodo_dias': dias,
        'total_lecturas': todos_los_registros.count(),
        'fecha_inicio': formatear_fecha(primer_registro.fecha_hora, solo_fecha=True) if primer_registro else '—',
    }


def formatear_fecha(dt, solo_fecha=False):
    if solo_fecha:
        return dt.strftime('%d/%m/%Y')
    return dt.strftime('%d/%m/%Y · %H:%M')


# 5) Datos para la gráfica comparativa (promedio diario)

def obtener_datos_comparativos(registros_periodo, desde, dias):
    agregados = (
        registros_periodo
        .annotate(dia=TruncDate('fecha_hora'))
        .values('dia')
        .annotate(
            temp_avg=Avg('temperatura'),
            hum_avg=Avg('humedad'),
            lux_avg=Avg('luminosidad'),
        )
        .order_by('dia')
    )

    if not agregados:
        return [], [], [], []

    # Mapear por fecha para rellenar días sin datos con None (evita huecos en el eje X)
    mapa = {a['dia']: a for a in agregados}

    hoy = timezone.now().date()
    fechas = [hoy - timedelta(days=i) for i in range(dias - 1, -1, -1)]

    etiquetas, temp_data, hum_data, lux_data = [], [], [], []
    for f in fechas:
        etiquetas.append(f.strftime('%d/%m'))
        a = mapa.get(f)
        temp_data.append(round(a['temp_avg'], 1) if a and a['temp_avg'] is not None else 0)
        hum_data.append(round(a['hum_avg'], 1) if a and a['hum_avg'] is not None else 0)
        lux_data.append(round(a['lux_avg'], 1) if a and a['lux_avg'] is not None else 0)

    return etiquetas, temp_data, hum_data, lux_data


# 6) Conteo de alertas según ConfiguracionAlarma del usuario

def obtener_resumen_alertas(usuario, registros_periodo):
    try:
        config = usuario.config_alarma
    except ConfiguracionAlarma.DoesNotExist:
        config = None

    if config is None:
        # Sin configuración: no se puede evaluar nada
        datos = []
        return datos, 0, {'clase': 'bajo', 'label': 'Bajo'}

    # Conteo de registros que violan cada umbral
    conteo_temp = registros_periodo.filter(temperatura__gt=config.temp_max).count() + registros_periodo.filter(temperatura__lt=config.temp_min).count()
    conteo_hum = registros_periodo.filter( humedad__gt=config.hum_max).count() + registros_periodo.filter(humedad__lt=config.hum_min).count()
    conteo_lux = registros_periodo.filter(luminosidad__gt=config.lux_max).count() + registros_periodo.filter( luminosidad__lt=config.lux_min).count()

    datos_crudos = [
        {'nombre': 'Temperatura', 'icono': 'bi-thermometer-high', 'color': 'rojo',  'conteo': conteo_temp},
        {'nombre': 'Humedad',     'icono': 'bi-droplet',          'color': 'azul',  'conteo': conteo_hum},
        {'nombre': 'Luminosidad', 'icono': 'bi-brightness-high',  'color': 'ambar', 'conteo': conteo_lux},
    ]

    total = sum(a['conteo'] for a in datos_crudos)

    # Si no hubo ninguna alerta, evitar divisiones por cero y mostrar 0%
    divisor = total if total > 0 else 1

    for a in datos_crudos:
        a['porcentaje'] = round(a['conteo'] / divisor * 100, 1)
        if a['conteo'] >= 6:
            a['riesgo_clase'], a['riesgo_label'] = 'alta', 'Alto'
        elif a['conteo'] >= 3:
            a['riesgo_clase'], a['riesgo_label'] = 'media', 'Medio'
        elif a['conteo'] >= 1:
            a['riesgo_clase'], a['riesgo_label'] = 'baja', 'Bajo'
        else:
            a['riesgo_clase'], a['riesgo_label'] = 'baja', 'Sin riesgo'

    # Riesgo global según total de alertas en el periodo
    if total >= 15:
        riesgo_global = {'clase': 'alto', 'label': 'Alto'}
    elif total >= 6:
        riesgo_global = {'clase': 'medio', 'label': 'Medio'}
    else:
        riesgo_global = {'clase': 'bajo', 'label': 'Bajo'}

    return datos_crudos, total, riesgo_global



# Generación de gráfica con Matplotlib

def generar_grafica_comparativa(etiquetas, temp_data, hum_data, lux_data):

    n = len(etiquetas)
    paso_etiqueta = max(1, n // 12)

    x = np.arange(n)
    ancho = 0.25

    fig, ax1 = plt.subplots(figsize=(11, 4), dpi=110)
    fig.patch.set_facecolor(COLOR_FONDO)
    ax1.set_facecolor(COLOR_FONDO)

    ax1.bar(x - ancho, temp_data, width=ancho, label='Temperatura (°C)', color=COLOR_TEMP)
    ax1.bar(x,         hum_data,  width=ancho, label='Humedad (%)',      color=COLOR_HUM)

    ax2 = ax1.twinx()
    ax2.bar(x + ancho, lux_data, width=ancho, label='Luminosidad (lux)', color=COLOR_LUX)

    for ax in (ax1, ax2):
        ax.set_facecolor(COLOR_FONDO)
        ax.tick_params(colors=COLOR_TEXTO_TENUE, labelsize=9)
        for spine in ax.spines.values():
            spine.set_visible(False)

    ax1.set_ylabel('°C / %', color=COLOR_TEXTO, fontsize=10)
    ax2.set_ylabel('lux', color=COLOR_TEXTO, fontsize=10)

    ax1.grid(axis='y', color=COLOR_FONDO_GRID, linewidth=0.8)
    ax1.set_axisbelow(True)

    ax1.set_xticks(x[::paso_etiqueta])
    ax1.set_xticklabels(
        [etiquetas[i] for i in range(0, n, paso_etiqueta)],
        color=COLOR_TEXTO_TENUE, fontsize=9
    )

    lineas1, etiquetas1 = ax1.get_legend_handles_labels()
    lineas2, etiquetas2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lineas1 + lineas2, etiquetas1 + etiquetas2,
        loc='upper center', bbox_to_anchor=(0.5, 1.18),
        ncol=3, frameon=False, fontsize=9, labelcolor=COLOR_TEXTO
    )

    fig.tight_layout()

    buffer = BytesIO()
    fig.savefig(buffer, format='png', facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode('utf-8')