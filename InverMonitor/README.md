# InverMonitor - Sistema de Monitoreo de Invernadero

InverMonitor es una plataforma web basada en Django diseñada para el monitoreo automatizado de variables climatológicas y de suelo en invernaderos. El sistema recibe datos en tiempo real desde una Raspberry Pi, procesa la información y la despliega mediante gráficas dinámicas e indicadores visuales a múltiples usuarios en simultáneo.



## Arquitectura y Funcionamiento del Proyecto

El proyecto está dividido en dos componentes principales que se comunican a través de internet:

1- Hardware (Raspberry Pi): Recopila las lecturas de los sensores físicos (Temperatura, Humedad Ambiental, Luminosidad y Humedad del Suelo) y las envía mediante peticiones HTTP POST hacia el servidor en la nube.

2-  Servidor Web (Django en PythonAnywhere): Cuenta con un endpoint API público (ViewApi.py) optimizado con una arquitectura multiusuario. Cada vez que la Raspberry Pi envía una lectura, el servidor clona automáticamente dicho registro para cada usuario registrado en el sistema. Esto garantiza que todos los clientes puedan visualizar el estado del invernadero en tiempo real desde sus propios paneles de control de manera independiente.



## Características Principales

1-  Autenticación Segura: Sistema de registro, inicio de sesión (Login) y cierre de sesión (Logout) para   los usuarios.

2- Dashboard de Temperatura y Luminosidad: Paneles individuales que muestran el valor actual, fecha/hora de la última lectura, estado de alerta (Alta/Baja/Normal) y la tendencia (Subiendo/Bajando/Estable).

3- Gráficas Dinámicas integradas: Generación de gráficas de línea temporales personalizadas mediante Matplotlib.

4- Historial Analítico: Tabla con los últimos 10 registros capturados y el cálculo automático de estadísticas (Máximos, Mínimos y Promedios).

5- Frecuencia AJAX: Actualización automática de datos en la interfaz web sin necesidad de recargar la página por completo.



## Tecnologías Utilizadas

- Backend: Python 3.x, Django Web Framework
- Frontend: HTML5, CSS3 (Plantilla con diseño oscuro/Dark Mode), JavaScript (AJAX / Fetch API)
- Visualización de Datos: Matplotlib (Renderizado en memoria mediante BytesIO y Base64)
- Base de Datos: SQLite / MySQL (Según entorno de despliegue)

---

## Instrucciones para Ejecutar el Proyecto

### 1. Requisitos Previos
Asegúrate de tener instalado Python en tu sistema. Se recomienda clonar el proyecto dentro de un entorno virtual.

### 2. Configuración del Servidor Django
Si deseas ejecutar el proyecto localmente o preparar el entorno en el host, sigue estos comandos en la terminal:

# Clonar el repositorio
git clone <https://github.com/yoselinuesfom/InverMonitorMIP155.git>
cd invermonitor

# Crear y activar un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows usa: venv\Scripts\activate

# Instalar las dependencias requeridas
pip install django matplotlib plotly django-crispy-forms

# Realizar las migraciones de la Base de Datos
python manage.py makemigrations
python manage.py migrate

# Crear un usuario Administrador (Superusuario)
python manage.py createsuperuser

# Iniciar el servidor local
python manage.py runserver