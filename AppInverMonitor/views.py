from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.db.models import Max, Min, Avg, Count
from django.http import JsonResponse
from datetime import timedelta
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from io import BytesIO
import base64
import plotly.graph_objects as go
from .forms import RegistrarUsuarioForm, LoginForm
from .models import RegistroSensor
import matplotlib
from io import BytesIO
import base64

def Home(request):
    return render(request, 'home.html')


def Desarrolladores(request):
    return render(request, 'desarrolladores.html')


def Documentacion(request):
    return render(request, 'documentacion.html')


def Register(request):
    if request.method == 'POST':
        form = RegistrarUsuarioForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada exitosamente.')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error al registrar usuario: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistrarUsuarioForm()

    return render(request, 'Register.html', {'form': form})


@never_cache
@require_http_methods(['GET', 'POST'])
def Ligin(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not form.cleaned_data.get('remember_me'):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)
            next_url = request.GET.get('next') or 'dashboard'
            return redirect(next_url)
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


@login_required
def Logout(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('dashboard')


# Helpers  Temperatura
def _calcular_estado(temp, config):
    if temp >= config.temp_max:
        return 'Alta'
    if temp <= config.temp_min:
        return 'Baja'
    return 'Normal'


def _calcular_tendencia(lecturas):
    if len(lecturas) < 2:
        return 'estable'
    diff = lecturas[0] - lecturas[1]
    if diff >  1.0:
        return 'subiendo'
    if diff < -1.0:
        return 'bajando'
    return 'estable'


def _delta_por_rango(rango):
    opciones = {
        '1h':  (timedelta(hours=1),  '%H:%M'),
        '24h': (timedelta(hours=24), '%H:%M'),
        '7d':  (timedelta(days=7),   '%d/%m %H:%M'),
        '30d': (timedelta(days=30),  '%d/%m'),
    }
    return opciones.get(rango, opciones['1h'])


def _construir_grafica(registros):
   
    fechas  = [timezone.localtime(r.fecha_hora) for r in registros]
    valores = [r.temperatura for r in registros]

    if not fechas:
        return None  # sin datos

    fig, ax = plt.subplots(figsize=(10, 3))
    fig.patch.set_facecolor('#0d1f12')   # fondo del canvas
    ax.set_facecolor('#0d1f12')          # fondo del área

    # Línea principal
    ax.plot(fechas, valores, color='#f0a500', linewidth=2, marker='o',
            markersize=3, zorder=3)

    # Relleno bajo la línea
    ax.fill_between(fechas, valores, alpha=0.08, color='#f0a500')

    # Estilos de ejes
    ax.tick_params(colors='#3d6e4f', labelsize=8)
    ax.yaxis.set_tick_params(labelcolor='#3d6e4f')
    ax.xaxis.set_tick_params(labelcolor='#3d6e4f')
    for spine in ax.spines.values():
        spine.set_edgecolor('#1a3a24')

    ax.grid(color='#1a3a24', linestyle='--', linewidth=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate(rotation=30)
    ax.set_ylabel('°C', color='#3d6e4f', fontsize=9)

    plt.tight_layout()

    # Convertir a base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100,
                facecolor=fig.get_facecolor())
    buffer.seek(0)
    imagen_b64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)

    return imagen_b64


# Vista Temperatura
@login_required(login_url='/login/')
def Temperatura(request):
    usuario = request.user
    config  = usuario.config_alarma
    rango   = request.GET.get('rango', '1h')

    # Lectura actual
    ultimo        = RegistroSensor.objects.filter(usuario=usuario).order_by('-fecha_hora').first()
    temp_actual   = ultimo.temperatura if ultimo else None
    fecha_lectura = timezone.localtime(ultimo.fecha_hora).strftime('%d/%m/%Y %I:%M %p') if ultimo else '—'
    estado_actual = _calcular_estado(temp_actual, config) if temp_actual is not None else '—'

    # Tendencia
    ultimas_3 = list(RegistroSensor.objects.filter(usuario=usuario).order_by('-fecha_hora').values_list('temperatura', flat=True)[:3])
    tendencia = _calcular_tendencia(ultimas_3)

    # Estadísticas
    stats = RegistroSensor.objects.filter(usuario=usuario).aggregate(
        maxima=Max('temperatura'), minima=Min('temperatura'),
        promedio=Avg('temperatura'), total_lecturas=Count('id'),
    )

    # Gráfica
    delta, _ = _delta_por_rango(rango)
    registros_grafica = RegistroSensor.objects.filter(usuario=usuario, fecha_hora__gte=timezone.now() - delta).order_by('fecha_hora')
    grafica_img = _construir_grafica(registros_grafica)

    # Historial
    historial_raw = list(RegistroSensor.objects.filter(usuario=usuario).order_by('-fecha_hora')[:10])
    historial = []
    for i, reg in enumerate(historial_raw):
        if i + 1 < len(historial_raw):
            diff = reg.temperatura - historial_raw[i + 1].temperatura
            tend_fila = 'subiendo' if diff > 1.0 else ('bajando' if diff < -1.0 else 'estable')
        else:
            tend_fila = 'estable'
        historial.append({
            'fecha_hora': timezone.localtime(reg.fecha_hora).strftime('%d/%m/%Y %I:%M %p'),
            'valor':      round(reg.temperatura, 1),
            'estado':     _calcular_estado(reg.temperatura, config),
            'tendencia':  tend_fila,
        })

    # Termómetro
    altura_termometro = min(max((temp_actual / 50) * 100, 2), 98) if temp_actual is not None else 0

    # Contexto
    contexto = {
        'temp_actual':       round(temp_actual, 1) if temp_actual else None,
        'fecha_lectura':     fecha_lectura,
        'estado_actual':     estado_actual,
        'tendencia':         tendencia,
        'altura_termometro': round(altura_termometro, 1),
        'stat_max':          round(stats['maxima'],   1) if stats['maxima']   else '—',
        'stat_min':          round(stats['minima'],   1) if stats['minima']   else '—',
        'stat_promedio':     round(stats['promedio'], 1) if stats['promedio'] else '—',
        'stat_lecturas':     stats['total_lecturas'],
        'grafica_img':       grafica_img,
        'rango_activo':      rango,
        'historial':         historial,
        'umbral_max':        config.temp_max,
        'umbral_min':        config.temp_min,
    }

    # AJAX — auto-refresh del JS
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'temp_actual':       contexto['temp_actual'],
            'estado_actual':     contexto['estado_actual'],
            'fecha_lectura':     contexto['fecha_lectura'],
            'tendencia':         contexto['tendencia'],
            'altura_termometro': contexto['altura_termometro'],
        })

    return render(request, 'temperatura.html', contexto)



#  Helper gráfica luminosidad 
def _construir_grafica_lux(registros):
    
    fechas  = [timezone.localtime(r.fecha_hora) for r in registros]
    valores = [r.luminosidad for r in registros]

    if not fechas:
        return None

    fig, ax = plt.subplots(figsize=(10, 3))
    fig.patch.set_facecolor('#0d1f12')
    ax.set_facecolor('#0d1f12')

    # Línea principal — color ámbar para luminosidad
    ax.plot(fechas, valores, color='#f0a500', linewidth=2,
            marker='o', markersize=3, zorder=3)

    # Relleno bajo la línea
    ax.fill_between(fechas, valores, alpha=0.08, color='#f0a500')

    # Estilos
    ax.tick_params(colors='#3d6e4f', labelsize=8)
    ax.yaxis.set_tick_params(labelcolor='#3d6e4f')
    ax.xaxis.set_tick_params(labelcolor='#3d6e4f')
    for spine in ax.spines.values():
        spine.set_edgecolor('#1a3a24')

    ax.grid(color='#1a3a24', linestyle='--', linewidth=0.5)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    fig.autofmt_xdate(rotation=30)
    ax.set_ylabel('lux', color='#3d6e4f', fontsize=9)

    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, facecolor=fig.get_facecolor())
    buffer.seek(0)
    imagen_b64 = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close(fig)

    return imagen_b64


#  Helper estado luminosidad 
def _calcular_estado_lux(lux, config):
    """Retorna 'Alta', 'Baja' o 'Normal' según los umbrales del usuario."""
    if lux >= config.lux_max:
        return 'Alta'
    if lux <= config.lux_min:
        return 'Baja'
    return 'Normal'


#  Helper tendencia luminosidad 
def _calcular_tendencia_lux(lecturas):
    """
    Recibe lista de floats (más reciente primero).
    Umbral: 50 lux de diferencia para considerar cambio.
    """
    if len(lecturas) < 2:
        return 'estable'
    diff = lecturas[0] - lecturas[1]
    if diff >  50:
        return 'subiendo'
    if diff < -50:
        return 'bajando'
    return 'estable'


#  Vista principal  
@login_required(login_url='/login/')
def Luminosidad(request):
    
    usuario = request.user
    config  = usuario.config_alarma
    rango   = request.GET.get('rango', '1h')

    # Lectura actual
    ultimo       = RegistroSensor.objects.filter(usuario=usuario).order_by('-fecha_hora').first()
    lux_actual   = ultimo.luminosidad if ultimo else None
    fecha_lectura = timezone.localtime(ultimo.fecha_hora).strftime('%d/%m/%Y %I:%M %p') if ultimo else '—'
    estado_actual = _calcular_estado_lux(lux_actual, config) if lux_actual is not None else '—'

    # Tendencia
    ultimas_3 = list(
        RegistroSensor.objects
        .filter(usuario=usuario)
        .order_by('-fecha_hora')
        .values_list('luminosidad', flat=True)[:3]
    )
    tendencia = _calcular_tendencia_lux(ultimas_3)

    # Estadísticas
    stats = RegistroSensor.objects.filter(usuario=usuario).aggregate(
        maxima=Max('luminosidad'),
        minima=Min('luminosidad'),
        promedio=Avg('luminosidad'),
        total_lecturas=Count('id'),
    )

    # Gráfica
    delta, _ = _delta_por_rango(rango)
    registros_grafica = (
        RegistroSensor.objects
        .filter(usuario=usuario, fecha_hora__gte=timezone.now() - delta)
        .order_by('fecha_hora')
    )
    grafica_img = _construir_grafica_lux(registros_grafica)

    # Historial
    historial_raw = list(
        RegistroSensor.objects
        .filter(usuario=usuario)
        .order_by('-fecha_hora')[:10]
    )
    historial = []
    for i, reg in enumerate(historial_raw):
        if i + 1 < len(historial_raw):
            diff = reg.luminosidad - historial_raw[i + 1].luminosidad
            tend_fila = 'subiendo' if diff > 50 else ('bajando' if diff < -50 else 'estable')
        else:
            tend_fila = 'estable'
        historial.append({
            'fecha_hora': timezone.localtime(reg.fecha_hora).strftime('%d/%m/%Y %I:%M %p'),
            'valor':      round(reg.luminosidad, 1),
            'estado':     _calcular_estado_lux(reg.luminosidad, config),
            'tendencia':  tend_fila,
        })

    contexto = {
        'lux_actual':    round(lux_actual, 1) if lux_actual is not None else None,
        'fecha_lectura': fecha_lectura,
        'estado_actual': estado_actual,
        'tendencia':     tendencia,
        'stat_max':      round(stats['maxima'],   1) if stats['maxima']   else '—',
        'stat_min':      round(stats['minima'],   1) if stats['minima']   else '—',
        'stat_promedio': round(stats['promedio'], 1) if stats['promedio'] else '—',
        'stat_lecturas': stats['total_lecturas'],
        'grafica_img':   grafica_img,
        'rango_activo':  rango,
        'historial':     historial,
        'umbral_max':    config.lux_max,
        'umbral_min':    config.lux_min,
    }

    # AJAX — auto-refresh del JS
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        from django.http import JsonResponse
        return JsonResponse({
            'lux_actual':    contexto['lux_actual'],
            'estado_actual': contexto['estado_actual'],
            'fecha_lectura': contexto['fecha_lectura'],
            'tendencia':     contexto['tendencia'],
        })

    return render(request, 'luminosidad.html', contexto)