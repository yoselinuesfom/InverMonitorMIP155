from django.urls import path
from django.contrib.auth import views as auth_views
from .import views
from .import viewHumedad
from .import viewConfiguracion
from .import viewHistorial
from .import viewPerfil
from .import viewEstadistica 
from .import viewDashboar
from .import viewHumedadSuelo
from .import viewNotificacione
from .import viewApi

urlpatterns = [
    path('', views.Home, name='home'),
    path('register/', views.Register, name='register'),
    path('dashboard/', viewDashboar.Dashboard, name='dashboard'),
    path('login/',  views.Ligin,  name='login'),
    path('logout/', views.Logout, name='logout'),
    path('desarrolladores/', views.Desarrolladores, name='desarrolladores'),
    path('documentacion/', views.Documentacion, name='documentacion'),
    path('password-reset/',auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('temperatura/', views.Temperatura, name='temperatura'),
    path('humedad/', viewHumedad.Humedad, name='humedad'),
    path('configuracion/', viewConfiguracion.Configuracion, name='configuracion'),
    path('historial/', viewHistorial.Historial, name='historial'),
    path('luminocidad/', views.Luminosidad, name='luminosidad' ),
    path('perfil/', viewPerfil.Perfil, name='perfil'),
    path('estadistica', viewEstadistica.Estadistica, name='estadistica'),
    path('humedadSuelo', viewHumedadSuelo.HumedadSuelo, name='humedadSuelo'),
    path('notificaciones', viewNotificacione.Notificaciones, name='notificaciones'),
    path('api/invermonitor/', viewApi.RecibirDatosSensor, name='apiInverMonitor')
]