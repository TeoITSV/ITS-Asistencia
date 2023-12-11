# mi_app/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('', home_view, name='base'),
    path('form/', form_view, name='form'),
    path('upload/', upload_files, name='upload_files'),
    path('informe/', informe_pdf_view, name='informe_pdf')
    # Puedes agregar más patrones de URL aquí si es necesario
]
