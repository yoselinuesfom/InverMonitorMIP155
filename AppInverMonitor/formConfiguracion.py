from django import forms
from .models import ConfiguracionAlarma

class ConfiguracionAlarmaForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionAlarma
        fields = [
            'temp_min', 'temp_max',
            'hum_min',  'hum_max',
            'lux_min',  'lux_max',
            'correo_alerta',         
        ]
        widgets = {
            'temp_min':       forms.NumberInput(attrs={'class': 'campo-input', 'step': '0.1'}),
            'temp_max':       forms.NumberInput(attrs={'class': 'campo-input', 'step': '0.1'}),
            'hum_min':        forms.NumberInput(attrs={'class': 'campo-input', 'step': '0.1'}),
            'hum_max':        forms.NumberInput(attrs={'class': 'campo-input', 'step': '0.1'}),
            'hum_min_suelo':  forms.NumberInput(attrs={'class': 'campo-input', 'step': '0.1'}),
            'hum_max_suelo':  forms.NumberInput(attrs={'class': 'campo-input', 'step': '0.1'}),
            'lux_min':        forms.NumberInput(attrs={'class': 'campo-input', 'step': '1'}),
            'lux_max':        forms.NumberInput(attrs={'class': 'campo-input', 'step': '1'}),
        }