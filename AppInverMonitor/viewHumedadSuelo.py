from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.db.models import Max, Min, Avg
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io, base64
from .models import RegistroSensor


def _generar_grafica(registros, umbral_min, umbral_max):
    """Genera la gráfica de humedad del suelo y retorna base64."""
    if not registros:
        return None

    fechas  = [r.fecha_hora for r in registros]
    valores = [r.humedad_suelo for r in registros]

    fig, ax = plt.subplots(figsize=(12, 4))
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#1e293b')

    ax.plot(fechas, valores, color='#22c55e', linewidth=2, zorder=3)
    ax.fill_between(fechas, valores, alpha=0.15, color='#22c55e')

    # Líneas de umbral
    ax.axhline(umbral_max, color='#ef4444', linewidth=1.2,
               linestyle='--', label=f'Máx {umbral_max}%')
    ax.axhline(umbral_min, color='#3b82f6', linewidth=1.2,
               linestyle='--', label=f'Mín {umbral_min}%')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %H:%M'))
    plt.xticks(rotation=30, color='#94a3b8', fontsize=8)
    plt.yticks(color='#94a3b8', fontsize=8)
    ax.set_ylabel('Humedad suelo (%)', color='#94a3b8', fontsize=9)
    ax.tick_params(colors='#94a3b8')
    for spine in ax.spines.values():
        spine.set_edgecolor('#334155')
    ax.legend(facecolor='#1e293b', labelcolor='#94a3b8', fontsize=8)
    ax.grid(True, color='#334155', linestyle='--', linewidth=0.5, alpha=0.5)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=120, facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode('utf-8')


@login_required(login_url='login')
def HumedadSuelo(request):
    usuario    = request.user
    rango      = request.GET.get('rango', '24h')
    ahora      = timezone.now()

    #  Rango de tiempo 
    rangos = {'1h': 1, '24h': 24, '7d': 168, '30d': 720}
    horas  = rangos.get(rango, 24)
    desde  = ahora - timedelta(hours=horas)

    #  Queries 
    registros_rango = RegistroSensor.objects.filter(
        usuario=usuario, fecha_hora__gte=desde
    ).order_by('fecha_hora')

    todos = RegistroSensor.objects.filter(usuario=usuario)
    ultimo = todos.first()   # ordering = ['-fecha_hora']

    #  Estadísticas globales 
    stats = todos.aggregate(
        maximo=Max('humedad_suelo'),
        minimo=Min('humedad_suelo'),
        promedio=Avg('humedad_suelo'),
    )

    #  Umbrales del usuario 
    try:
        config     = usuario.config_alarma
        umbral_min = config.suelo_min
        umbral_max = config.suelo_max
    except Exception:
        umbral_min, umbral_max = 20.0, 70.0

    # Estado actual 
    valor_actual = ultimo.humedad_suelo if ultimo else None
    if valor_actual is None:
        estado_actual = 'Sin datos'
    elif valor_actual > umbral_max:
        estado_actual = 'Alta'
    elif valor_actual < umbral_min:
        estado_actual = 'Baja'
    else:
        estado_actual = 'Normal'

    fecha_lectura = ultimo.fecha_hora.strftime('%d/%m/%Y %H:%M:%S') if ultimo else None

    # Tendencia 
    recientes = list(todos[:2])
    tendencia = 'estable'
    if len(recientes) == 2:
        diff = recientes[0].humedad_suelo - recientes[1].humedad_suelo
        if diff > 1:
            tendencia = 'subiendo'
        elif diff < -1:
            tendencia = 'bajando'

    #  Historial últimas 10 con tendencia fila a fila
    ultimas_10 = list(todos[:10])
    historial  = []
    for i, reg in enumerate(ultimas_10):
        val = reg.humedad_suelo
        if val > umbral_max:
            estado = 'Alta'
        elif val < umbral_min:
            estado = 'Baja'
        else:
            estado = 'Normal'

        if i < len(ultimas_10) - 1:
            diff_h = val - ultimas_10[i + 1].humedad_suelo
            if diff_h > 1:
                tend_fila = 'subiendo'
            elif diff_h < -1:
                tend_fila = 'bajando'
            else:
                tend_fila = 'estable'
        else:
            tend_fila = 'estable'

        historial.append({
            'fecha_hora': reg.fecha_hora.strftime('%d/%m/%Y %H:%M'),
            'valor':      round(val, 1),
            'estado':     estado,
            'tendencia':  tend_fila,
        })

    #  Gráfica 
    grafica_img = _generar_grafica(
        list(registros_rango), umbral_min, umbral_max
    )

    context = {
        'suelo_actual':  round(valor_actual, 1) if valor_actual is not None else None,
        'estado_actual': estado_actual,
        'fecha_lectura': fecha_lectura,
        'umbral_min':    umbral_min,
        'umbral_max':    umbral_max,
        'stat_max':      round(stats['maximo'],   1) if stats['maximo']   else '—',
        'stat_min':      round(stats['minimo'],   1) if stats['minimo']   else '—',
        'stat_promedio': round(stats['promedio'], 1) if stats['promedio'] else '—',
        'stat_lecturas': todos.count(),
        'tendencia':     tendencia,
        'historial':     historial,
        'grafica_img':   grafica_img,
        'rango_activo':  rango,
    }
    return render(request, 'humedadSuelo.html', context)