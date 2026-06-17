from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from AppInverMonitor.models import RegistroSensor
import time

class Command(BaseCommand):
    help = 'Simula datos'

    def handle(self, *args, **kwargs):
        usuario = User.objects.first()
        if not usuario:
            self.stdout.write('No hay usuarios')
            return
        simulaciones = [
            (25.0, 60.0, 5000, 45.0, 'Todo normal'),
            (40.0, 60.0, 5000, 45.0, 'Temperatura alta'),
            (10.0, 60.0, 5000, 45.0, 'Temperatura baja'),
            (25.0, 60.0, 5000, 10.0, 'Suelo seco'),
            (40.0, 30.0, 5000, 10.0, 'Varias alertas'),
        ]
        for temp, hum, luz, suelo, desc in simulaciones:
            RegistroSensor.objects.create(
                usuario=usuario,
                temperatura=temp,
                humedad=hum,
                luminosidad=luz,
                humedad_suelo=suelo,
            )
            self.stdout.write(f'{desc} -> temp={temp} hum={hum} luz={luz} suelo={suelo}')
            time.sleep(2)
        self.stdout.write('Simulacion completa')
