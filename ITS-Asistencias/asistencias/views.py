from django.shortcuts import render,redirect
from asistencias.forms import UploadForm
from asistencias.funciones import *
import pandas as pd

# Create your views here.


def home_view(request):
    return render(request, 'stats.html')

def form_view(request):
    return render(request, 'form.html')

def upload_files(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            horarios_file = form.cleaned_data['horarios_file']
            marcas_file = form.cleaned_data['marcas_file']
            leerPlanillaHorarios(horarios_file)
            return redirect('base')
    else:
        # Si hay parámetros en la URL, intenta prellenar el formulario
        form = UploadForm(initial={
            'horarios_file': request.GET.get('horarios_file', ''),
            'marcas_file': request.GET.get('marcas_file', ''),
        })

    return render(request, 'form.html', {'form': form})
