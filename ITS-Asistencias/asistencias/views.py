from django.shortcuts import render,redirect
from asistencias.forms import UploadForm, InformeForm
from asistencias.funciones import *
import locale
import pandas as pd
from django.views.decorators.cache import cache_page
import json 
from django.http import JsonResponse, StreamingHttpResponse
# Create your views here.



#@cache_page(60 * 15)  # Cachear durante 15 minutos
def home_view(request):
    print("aaa")
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

            def event_stream():
                success_flag = True
                try:
                    if horarios_file:
                        yield 'Starting to read schedules...\n'
                        for success, message in leerPlanillaHorarios(horarios_file):
                            yield message + '\n'
                            if not success:
                                success_flag = False
                                return
                        yield 'Finished reading schedules.\n'
                    else:
                        yield 'No se modifico ningun Horario\n'
                    
                    if marcas_file:
                        yield 'Starting to read marcas...\n'
                        for success, message in leerPlanillaMarcas(marcas_file):
                            yield message + '\n'
                            if not success:
                                success_flag = False
                                return
                        yield 'Finished reading marcas.\n'
                    else:
                        yield 'No se agrego ninguna Marca.\n'

                    if success_flag:
                        yield 'All tasks completed successfully.\n'
                    else:
                        yield 'Some tasks failed.\n'
                except Exception as e:
                    yield f'An error occurred: {str(e)}\n'

            response = StreamingHttpResponse(event_stream(), content_type='text/plain')
            response['Cache-Control'] = 'no-cache'
            response['Content-Type'] = 'text/plain; charset=utf-8'
            return response

    else:
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


