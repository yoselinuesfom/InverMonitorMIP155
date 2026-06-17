from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"


class ConfiguracionAlarma(models.Model):
    usuario       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='config_alarma')
    temp_max      = models.FloatField(default=35.0)
    temp_min      = models.FloatField(default=15.0)
    hum_max       = models.FloatField(default=80.0)
    hum_min       = models.FloatField(default=40.0)
    lux_max       = models.IntegerField(default=60000)
    lux_min       = models.IntegerField(default=10)
    suelo_min     = models.FloatField(default=20.0)
    suelo_max     = models.FloatField(default=70.0)
    correo_alerta = models.EmailField(blank=True)

    class Meta:
        verbose_name = "Configuración de Alarma"
        verbose_name_plural = "Configuraciones de Alertas"

    def __str__(self):
        return f"Config. Alertas — {self.usuario.username}"


class RegistroSensor(models.Model):
    usuario       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registros')
    fecha_hora    = models.DateTimeField(auto_now_add=True, db_index=True)
    temperatura   = models.FloatField()
    humedad       = models.FloatField()
    luminosidad   = models.IntegerField()
    humedad_suelo = models.FloatField()

    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = "Registro de Sensor"
        verbose_name_plural = "Registros de Sensor"

    def __str__(self):
        return f"Medición #{self.id} — {self.usuario.username} — {self.fecha_hora:%Y-%m-%d %H:%M}"


class NotificacionAlerta(models.Model):
    SENSOR_CHOICES = [
        ('temperatura',   'Temperatura'),
        ('humedad',       'Humedad'),
        ('luminosidad',   'Luminosidad'),
        ('humedad_suelo', 'Humedad del Suelo'),
    ]
    TIPO_CHOICES = [
        ('alta', 'Crítica Alta'),
        ('baja', 'Crítica Baja'),
    ]

    usuario          = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    sensor           = models.CharField(max_length=20, choices=SENSOR_CHOICES)
    tipo             = models.CharField(max_length=4,  choices=TIPO_CHOICES)
    valor            = models.FloatField()
    umbral_min       = models.FloatField()
    umbral_max       = models.FloatField()
    correo_enviado_a = models.EmailField()
    fecha_hora       = models.DateTimeField(auto_now_add=True, db_index=True)
    leida            = models.BooleanField(default=False)

    class Meta:
        ordering = ['-fecha_hora']
        verbose_name = "Notificación de Alerta"
        verbose_name_plural = "Notificaciones de Alertas"

    def __str__(self):
        return f"{self.get_sensor_display()} {self.get_tipo_display()} — {self.usuario.username} — {self.fecha_hora:%Y-%m-%d %H:%M}"


# Signals 

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def crear_config_alarma(sender, instance, created, **kwargs):
    if created:
        ConfiguracionAlarma.objects.create(
            usuario=instance,
            correo_alerta=instance.email or ''
        )

@receiver(post_save, sender=RegistroSensor)
def verificar_alertas_sensor(sender, instance, created, **kwargs):
    if not created:
        return

    usuario = instance.usuario
    try:
        config = usuario.config_alarma
    except ConfiguracionAlarma.DoesNotExist:
        return

    correo_destino = config.correo_alerta or usuario.email
    if not correo_destino:
        print(f"Sin correo para {usuario.username}")
        return

    anomalias = []

    if instance.temperatura > config.temp_max:
        anomalias.append({'sensor': 'temperatura', 'tipo': 'alta', 'valor': instance.temperatura,
            'umbral_min': config.temp_min, 'umbral_max': config.temp_max,
            'texto': f"Temperatura CRÍTICA ALTA: {instance.temperatura}°C (Máx: {config.temp_max}°C)"})
    elif instance.temperatura < config.temp_min:
        anomalias.append({'sensor': 'temperatura', 'tipo': 'baja', 'valor': instance.temperatura,
            'umbral_min': config.temp_min, 'umbral_max': config.temp_max,
            'texto': f"Temperatura CRÍTICA BAJA: {instance.temperatura}°C (Mín: {config.temp_min}°C)"})

    if instance.humedad > config.hum_max:
        anomalias.append({'sensor': 'humedad', 'tipo': 'alta', 'valor': instance.humedad,
            'umbral_min': config.hum_min, 'umbral_max': config.hum_max,
            'texto': f"Humedad CRÍTICA ALTA: {instance.humedad}% (Máx: {config.hum_max}%)"})
    elif instance.humedad < config.hum_min:
        anomalias.append({'sensor': 'humedad', 'tipo': 'baja', 'valor': instance.humedad,
            'umbral_min': config.hum_min, 'umbral_max': config.hum_max,
            'texto': f"Humedad CRÍTICA BAJA: {instance.humedad}% (Mín: {config.hum_min}%)"})

    if instance.luminosidad > config.lux_max:
        anomalias.append({'sensor': 'luminosidad', 'tipo': 'alta', 'valor': instance.luminosidad,
            'umbral_min': config.lux_min, 'umbral_max': config.lux_max,
            'texto': f"Luminosidad CRÍTICA ALTA: {instance.luminosidad} Lx (Máx: {config.lux_max} Lx)"})
    elif instance.luminosidad < config.lux_min:
        anomalias.append({'sensor': 'luminosidad', 'tipo': 'baja', 'valor': instance.luminosidad,
            'umbral_min': config.lux_min, 'umbral_max': config.lux_max,
            'texto': f"Luminosidad CRÍTICA BAJA: {instance.luminosidad} Lx (Mín: {config.lux_min} Lx)"})

    if instance.humedad_suelo > config.suelo_max:
        anomalias.append({'sensor': 'humedad_suelo', 'tipo': 'alta', 'valor': instance.humedad_suelo,
            'umbral_min': config.suelo_min, 'umbral_max': config.suelo_max,
            'texto': f"Humedad suelo CRÍTICA ALTA: {instance.humedad_suelo}% (Máx: {config.suelo_max}%)"})
    elif instance.humedad_suelo < config.suelo_min:
        anomalias.append({'sensor': 'humedad_suelo', 'tipo': 'baja', 'valor': instance.humedad_suelo,
            'umbral_min': config.suelo_min, 'umbral_max': config.suelo_max,
            'texto': f"Humedad suelo CRÍTICA BAJA: {instance.humedad_suelo}% (Mín: {config.suelo_min}%)"})

    if not anomalias:
        return

    for a in anomalias:
        NotificacionAlerta.objects.create(
            usuario          = usuario,
            sensor           = a['sensor'],
            tipo             = a['tipo'],
            valor            = a['valor'],
            umbral_min       = a['umbral_min'],
            umbral_max       = a['umbral_max'],
            correo_enviado_a = correo_destino,
        )

    asunto = f"ALERTA INVERNADERO — {usuario.username}"
    cuerpo = (
        f"Estimado/a {usuario.username},\n\n"
        f"Se han detectado lecturas fuera de los rangos óptimos en tu invernadero.\n\n"
        f"Detalles de las anomalías:\n"
        + "".join(f"  • {a['texto']}\n" for a in anomalias)
        + f"\nFecha y Hora: {instance.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Revisa tu panel en InverMonitor.\n\n"
        f"Atentamente,\nSistema Automatizado InverMonitor."
    )

    try:
        send_mail(
            subject=asunto, message=cuerpo,
            from_email=None, recipient_list=[correo_destino],
            fail_silently=False,
        )
        print(f"Correo enviado a {correo_destino} ({len(anomalias)} anomalías)")
    except Exception as e:
        print(f"Error al enviar correo: {e}")