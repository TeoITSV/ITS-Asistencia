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
    form = InformeForm()
    if request.method == 'POST':
        form = InformeForm(request.POST)
        if form.is_valid():
            success_flag = True
            fechaInicio = form.cleaned_data['fechaInicio']
            fechaFin = form.cleaned_data['fechaFin']
            empleados = form.cleaned_data['empleados']
            margenEntrada = form.cleaned_data['margenEntrada']
            empleados = [Empleado.objects.get(idEmpleado=empleado) for empleado in empleados]
            print(f'Fecha Inicio: {fechaInicio}')
            print(f'Fecha Fin: {fechaFin}')
            print(f'Empleados: {empleados}')
            print(f'Margen Entrada: {margenEntrada}')

            return render(request, 'informepdf.html', {'form': form, 'success_flag': success_flag})
        else:
            # Crea una instancia del formulario con valores por defecto
            initial_data = {
                'fechaInicio': '2023-01-01',
                'fechaFin': '2023-01-31',
                'empleados': [],
                'margenEntrada': '08:00:00',
            }
            form = InformeForm(initial=initial_data)

    return render(request, 'informepdf.html', {'form': form})
