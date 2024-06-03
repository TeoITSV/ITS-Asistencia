from django.shortcuts import render,redirect
from asistencias.forms import UploadForm, InformeForm
from asistencias.funciones import *
import locale
import pandas as pd
from django.views.decorators.cache import cache_page
import json 
from django.http import JsonResponse, StreamingHttpResponse
# Create your views here.



@cache_page(60 * 15)  # Cachear durante 15 minutos
def home_view(request):
    total_retrasos, total_salidas_tempranas = calcStats(None, None)
    histograma = HistogramaHome()
    marcasxanio = histograma.marcasAnio()
    faltasxanio = histograma.faltasAnio()

    pieChart = PieChartHome()
    dataPieChart = pieChart.calcStats()
    return render(request, 'stats.html',{'total_empleados': Empleado.objects.count(),
                                          'total_marcas': Marca.objects.count(),
                                          'total_retrasos': total_retrasos,
                                        'total_salidas_anticipadas': total_salidas_tempranas,
                                        'marcasxanio': marcasxanio,
                                        'faltasxanio': faltasxanio,
                                        'dataPieChart': dataPieChart
                                        })

def form_view(request):
    return render(request, 'form.html')

def upload_files(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            horarios_file = form.cleaned_data['horarios_file']
            marcas_file = form.cleaned_data['marcas_file']
            if horarios_file:
                successHorarios, messageHorarios = leerPlanillaHorarios(horarios_file)
            else:
                successHorarios = True
                messageHorarios = f'No se modifico ningun Horario\n'
            if marcas_file:
                successMarcas, messageMarcas = leerPlanillaMarcas(marcas_file)
            else:
                successMarcas = True
                messageMarcas = f'No se agrego ninguna Marca. \n'
            if successHorarios == True and successMarcas == True:
                success_flag = True
            else:
                success_flag = False
            message = f"{messageHorarios}. \n {messageMarcas}"
            return render(request, 'form.html', {'form': form, 'success_flag': success_flag,'message': message})
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


