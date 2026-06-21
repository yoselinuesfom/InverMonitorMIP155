import base64
from io import BytesIO
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Max, Min
from django.shortcuts import render
from django.utils import timezone
import matplotlib 
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .models import RegistroSensor


# Paleta  de colores
COLOR_FONDO       = '#111f15'
COLOR_FONDO_GRID  = '#162a1c'
COLOR_TEXTO       = '#7aab8a'
COLOR_TEXTO_TENUE = '#3d6e4f'
COLOR_HUM         = '#3daaf0'

RANGOS_HORAS = {'1h': 1, '24h': 24, '7d': 24 * 7, '30d': 24 * 30}

@login_required(login_url='login')
def Humedad(request):
    usuario = request.user
    rango_activo = request.GET.get('rango', '24h')
    horas = RANGOS_HORAS.get(rango_activo, 24)

    desde = timezone.now() - timedelta(hours=horas)

    todos_los_registros = RegistroSensor.objects.filter(usuario=usuario)
    registros_rango = todos_los_registros.filter(fecha_hora__gte=desde).order_by('fecha_hora')

    # ──────────────────────────────────────────
    # Configuración de umbrales del usuario
    # ──────────────────────────────────────────
    try:
        config = usuario.config_alarma
        umbral_min = config.hum_min
        umbral_max = config.hum_max
    except AttributeError:
        umbral_min, umbral_max = 40.0, 80.0

    # ──────────────────────────────────────────
    # Última lectura 
    # ──────────────────────────────────────────
    ultima = todos_los_registros.first()  # ordering = ['-fecha_hora']

    hum_actual    = round(ultima.humedad, 1) if ultima else None
    fecha_lectura = ultima.fecha_hora.strftime('%d/%m/%Y · %H:%M') if ultima else None

    if hum_actual is None:
        estado_actual = 'Normal'
    elif hum_actual > umbral_max:
        estado_actual = 'Alta'
    elif hum_actual < umbral_min:
        estado_actual = 'Baja'
    else:
        estado_actual = 'Normal'

    # ──────────────────────────────────────────
    # Tendencia: comparar última lectura vs penúltima
    # ──────────────────────────────────────────
    penultima = todos_los_registros.all()[1] if todos_los_registros.count() > 1 else None
    tendencia = 'estable'
    if ultima and penultima:
        diferencia = ultima.humedad - penultima.humedad
        if diferencia > 1:
            tendencia = 'subiendo'
        elif diferencia < -1:
            tendencia = 'bajando'

    # ──────────────────────────────────────────
    # Estadísticas del periodo seleccionado
    # ──────────────────────────────────────────
    stats = registros_rango.aggregate(
        max_val=Max('humedad'),
        min_val=Min('humedad'),
        avg_val=Avg('humedad'),
    )
    stat_max      = round(stats['max_val'], 1) if stats['max_val'] is not None else '—'
    stat_min      = round(stats['min_val'], 1) if stats['min_val'] is not None else '—'
    stat_promedio = round(stats['avg_val'], 1) if stats['avg_val'] is not None else '—'
    stat_lecturas = registros_rango.count()

    # ──────────────────────────────────────────
    # Gráfica de evolución
    # ──────────────────────────────────────────
    grafica_img = None
    if registros_rango.exists():
        grafica_img = generar_grafica_humedad(registros_rango, rango_activo)

    # ──────────────────────────────────────────
    # Historial reciente últimas 10 lecturas con estado y tendencia
    # ──────────────────────────────────────────
    historial = construir_historial(todos_los_registros[:10], umbral_min, umbral_max)

    contexto = {
        'hum_actual': hum_actual,
        'estado_actual': estado_actual,
        'umbral_min': umbral_min,
        'umbral_max': umbral_max,
        'fecha_lectura': fecha_lectura,
        'rango_activo': rango_activo,
        'grafica_img': grafica_img,
        'stat_max': stat_max,
        'stat_min': stat_min,
        'stat_promedio': stat_promedio,
        'stat_lecturas': stat_lecturas,
        'tendencia': tendencia,
        'historial': historial,
    }
    return render(request, 'humedad.html', contexto)


# ──────────────────────────────────────────────
# Historial con estado y tendencia por fila
# ──────────────────────────────────────────────
def construir_historial(registros, umbral_min, umbral_max):
    registros = list(registros)
    historial = []

    for i, reg in enumerate(registros):
        valor = reg.humedad

        if valor > umbral_max:
            estado = 'Alta'
        elif valor < umbral_min:
            estado = 'Baja'
        else:
            estado = 'Normal'

        # Comparar contra el registro anterior cronológicamente 
        tendencia = 'estable'
        if i + 1 < len(registros):
            anterior = registros[i + 1].humedad
            diferencia = valor - anterior
            if diferencia > 1:
                tendencia = 'subiendo'
            elif diferencia < -1:
                tendencia = 'bajando'

        historial.append({
            'fecha_hora': reg.fecha_hora.strftime('%d/%m · %H:%M'),
            'valor': round(valor, 1),
            'estado': estado,
            'tendencia': tendencia,
        })

    return historial


# ──────────────────────────
# Gráfica de evolución línea 
# ──────────────────────────
def generar_grafica_humedad(registros_rango, rango_activo):
    registros = list(registros_rango)

    valores = [r.humedad for r in registros]

    if rango_activo in ('1h', '24h'):
        fmt = '%H:%M'
    else:
        fmt = '%d/%m'

    etiquetas = [r.fecha_hora.strftime(fmt) for r in registros]

    n = len(etiquetas)
    paso_etiqueta = max(1, n // 12)

    fig, ax = plt.subplots(figsize=(11, 3.2), dpi=110)
    fig.patch.set_facecolor(COLOR_FONDO)
    ax.set_facecolor(COLOR_FONDO)

    x = range(n)
    ax.plot(x, valores, color=COLOR_HUM, linewidth=1.8)
    ax.fill_between(x, valores, color=COLOR_HUM, alpha=0.15)

    ax.set_facecolor(COLOR_FONDO)
    ax.tick_params(colors=COLOR_TEXTO_TENUE, labelsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_ylabel('Humedad (%)', color=COLOR_TEXTO, fontsize=10)
    ax.grid(axis='y', color=COLOR_FONDO_GRID, linewidth=0.8)
    ax.set_axisbelow(True)

    ax.set_xticks(list(x)[::paso_etiqueta])
    ax.set_xticklabels([etiquetas[i] for i in range(0, n, paso_etiqueta)],
                        color=COLOR_TEXTO_TENUE, fontsize=9)

    fig.tight_layout()

    buffer = BytesIO()
    fig.savefig(buffer, format='png', facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode('utf-8')