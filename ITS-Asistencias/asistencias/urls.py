# mi_app/urls.py
from django.urls import path
from .views import mi_vista

urlpatterns = [
    path('', mi_vista, name='base'),
    # Puedes agregar más patrones de URL aquí si es necesario
]
