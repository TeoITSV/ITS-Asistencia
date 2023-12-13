from django.shortcuts import render,redirect
from asistencias.forms import UploadForm, InformeForm
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
            leerPlanillaMarcas(marcas_file)
            success_flag = True
            return render(request, 'form.html', {'form': form, 'success_flag': success_flag})
    else:
        # Si hay parámetros en la URL, intenta prellenar el formulario
        form = UploadForm(initial={
            'horarios_file': request.GET.get('horarios_file', ''),
            'marcas_file': request.GET.get('marcas_file', ''),
        })

    return render(request, 'form.html', {'form': form})

def informe_pdf_view(request):
    initial_data = {
                'fechaInicio': datetime.today().replace(day=1,month=1),
                'fechaFin': (datetime.today().replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1),
                'selectAll':'todos',
                'empleados': [],
                'minutos': 0,
                'segundos':0
            }
    formInit = InformeForm(initial=initial_data)
    formInit.fields['empleados'].choices = [(empleado.idEmpleado, empleado.nombreCompleto) for empleado in Empleado.objects.filter(estaActivo=True)]
    
    if request.method == 'POST':
        form = InformeForm(request.POST)
        if form.is_valid():
            success_flag = True
            return generarInforme(form)
        else:
            # Crea una instancia del formulario con valores por defecto
            
            form = InformeForm(initial=initial_data)

    return render(request, 'informepdf.html', {'form': formInit})
