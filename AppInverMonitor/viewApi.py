from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import RegistroSensor  

@csrf_exempt
def RecibirDatosSensor(request):
    if request.method == 'POST':
        try:
            temp  = float(request.POST.get('temperatura', 0))
            hum   = float(request.POST.get('humedad', 0))
            luz   = float(request.POST.get('luminosidad', 0))
            suelo = float(request.POST.get('humedad_suelo', 0))

            from django.contrib.auth.models import User 
            usuario = User.objects.first()  
            
            nuevo_registro = RegistroSensor.objects.create(
                usuario       = usuario, 
                temperatura   = temp,
                humedad       = hum,
                luminosidad   = luz,
                humedad_suelo = suelo
            )

            return JsonResponse({
                'status': 'success',
                'registro_id': nuevo_registro.id
            }, status=201)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)