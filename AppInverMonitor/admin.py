from django.contrib import admin

# Register your models here.

from .models import PerfilUsuario
from .models import ConfiguracionAlarma
from .models import RegistroSensor

admin.site.register(PerfilUsuario)
admin.site.register(ConfiguracionAlarma)
admin.site.register(RegistroSensor)

