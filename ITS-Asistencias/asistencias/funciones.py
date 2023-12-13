from datetime import datetime, timedelta,time
import json
import locale
import openpyxl

import pytz
from asistencias.models import *
from django.utils import timezone
import pandas as pd
from collections import defaultdict
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Alignment
from openpyxl.worksheet.table import Table, TableStyleInfo

def crearEmpleadoFila(row):
    empleado_nombre = row['Nombre']
    empleado_id = row['ID de usuario']
    if empleado_nombre is not None and empleado_id is not None and empleado_nombre != 'vacio' and empleado_id != 'vacio':
        empleado, created = Empleado.objects.get_or_create(nombreCompleto=empleado_nombre, idEmpleado=empleado_id )
        if created:
            empleado.save()
        return empleado
    return None
def crearHorario(empleado):
    horariosViejos = Horario.objects.filter(empleado=empleado,esActual=True)
    #Borrado logico de los horarios viejos
    for horarioActual in horariosViejos:
        horarioActual.esActual = False
        horarioActual.fechaBajada = timezone.make_aware(datetime.now())
        horarioActual.save()
    #Creacion del horario nuevo
    horario = Horario(empleado=empleado)
    horario.save()
    return horario

def crearDiaHorario(horario,dia,valor_in,valor_out):
    if Horario.objects.filter(id=horario.id).exists():
        if valor_in != 'vacio' and valor_out != 'vacio':
            diaHorario = DiaHorario(horario=horario,diaNombre=dia,horaEntrada=valor_in,horaSalida=valor_out)
        else:
            diaHorario = DiaHorario(horario=horario,diaNombre=dia)
        diaHorario.save()
        return diaHorario
             
def crearHorarioFila(row,horarios_df, empleado):
    horario = crearHorario(empleado)

    for dia in Dia.objects.all():
        columna_in = dia.nombre
        valor_columna_in = row[dia.nombre]
        
        # Obtener la posición de la columna actual en el DataFrame
        posicion_columna_in = horarios_df.columns.get_loc(columna_in)
        
        # Obtener el nombre de la columna a la derecha
        columna_out = horarios_df.columns[posicion_columna_in + 1] if posicion_columna_in < len(horarios_df.columns) - 1 else None
        valor_columna_out = row[columna_out] if columna_out is not None else None
        #Aca se crea el Horario con sus diaHorario
        #faltaria una validacion para no crear horarios duplicados
        crearDiaHorario(horario,dia,valor_columna_in,valor_columna_out)


def crearMarca(diaHorario,empleado, fechaHora, tipoMarca):
    if tipoMarca:
        tipoMarca = TipoMarca.objects.filter(nombre=tipoMarca).first()
    else:
        tipoMarca = None
    marca, created = Marca.objects.get_or_create(diaHorario=diaHorario,empleado=empleado,fechaHora=timezone.make_aware(fechaHora),tipoMarca=tipoMarca)
    marcas = Marca.objects.filter(diaHorario=diaHorario,empleado=empleado,fechaHora=timezone.make_aware(fechaHora))
    if created:
        marca.save()
        return marca
    return marca
def parseMarcas(df):
    
    # Crea un diccionario para almacenar las marcas de tiempo por fecha
    data_dict = defaultdict(lambda: {'Nombre': '', 'marcas': defaultdict(list)})

    # Itera sobre las filas del DataFrame
    for index, row in df.iterrows():
        id_empleado = row['ID de usuario']
        nombre_empleado = row['Nombre']
        fecha_hora = row['Fecha/Hora']

        # Convierte el objeto Timestamp a una cadena y luego extrae la fecha
        fecha = fecha_hora.strftime('%m/%d/%y').split()[0]

        # Almacena el nombre del empleado en el diccionario
        data_dict[id_empleado]['Nombre'] = nombre_empleado

        # Agrega la marca de tiempo a la lista correspondiente en el diccionario
        data_dict[id_empleado]['marcas'][fecha].append(str(fecha_hora))

    # Convierte el diccionario a una lista de diccionarios
    marcasEmpleadoPorDia = [{'ID de usuario': k, 'Nombre': v['Nombre'], 'marcas': v['marcas']} for k, v in data_dict.items()]
    return marcasEmpleadoPorDia
def crearMarcaEmpleado(empleado, dicMarcas):
    # Se busca el horario actual del empleado
    horario_actual = Horario.objects.filter(empleado=empleado,esActual=True).latest('fechaCreacion')

    for dia, marcas in dicMarcas['marcas'].items():
        fecha_dt = datetime.strptime(dia, "%m/%d/%y")
        nombre_dia_semana = fecha_dt.strftime("%A").capitalize()
        fecha_formateada = fecha_dt.strftime("%Y/%m/%d")

        # Se busca el día y horario correspondiente
        dia_horario_actual = DiaHorario.objects.filter(horario=horario_actual, diaNombre__nombre=nombre_dia_semana).first()
        # Convierte las marcas a objetos datetime
        marcas_dt = [datetime.strptime(marca, '%Y-%m-%d %H:%M:%S') for marca in marcas]
        # Obtén la hora de entrada y salida del horario actual
        print(f'fecha_dt: {fecha_dt} - dia_horario_actual: {dia_horario_actual.horaEntrada}')
        hora_entrada_horario = datetime.combine(fecha_dt.date(), dia_horario_actual.horaEntrada)
        hora_salida_horario = datetime.combine(fecha_dt.date(), dia_horario_actual.horaSalida)
# aa
        marcaMax = max(marcas_dt)
        marcaMin = min(marcas_dt)
        tipoEntrada = None
        igual = False
        if marcaMax == marcaMin or len(marcas_dt) == 1:
            igual = True
            diferenciaHorarioIn = hora_entrada_horario - marcaMax
            diferenciaHorarioOut = hora_salida_horario - marcaMax
            if diferenciaHorarioIn < diferenciaHorarioOut:
                tipoEntrada = 'In'
            elif diferenciaHorarioIn > diferenciaHorarioOut:
                tipoEntrada = 'Out'
            else:
                tipoEntrada = None
            crearMarca(dia_horario_actual,empleado, marcaMax, tipoEntrada)
        else:
            crearMarca(dia_horario_actual,empleado, marcaMin, 'In')
            crearMarca(dia_horario_actual,empleado, marcaMax, 'Out')
        for marca in marcas_dt:
            if marca!= marcaMax and marca!= marcaMin and igual != True:
                crearMarca(dia_horario_actual,empleado, marca, None)
def validarHorario(row, empleado, horarios_df):
    # implementar logica en un futuro para evitar entradas duplicadas el mismo dia
    horarios = Horario.objects.filter(empleado=empleado,esActual=True)
    if horarios.count() == 0:
        return True
    horario_dict = defaultdict(lambda: {'horario': None, 'diasHorario': []})

    # Llenar el diccionario con información sobre los horarios y sus días asociados
    for horario in horarios:
        diasHorario = DiaHorario.objects.filter(horario=horario)
        horario_dict[horario]['horario'] = horario
        horario_dict[horario]['diasHorario'].extend(diasHorario)
    # Imprimir los días de horario para cada horario
    for diaHorario in horario_dict[horario]['diasHorario']:
        dia = diaHorario.diaNombre.nombre
        if diaHorario.horaEntrada is None:
            diaHorario.horaEntrada = 'vacio'
        if diaHorario.horaSalida is None:
            diaHorario.horaSalida = 'vacio'
        columna_in = dia
        valor_columna_in = row[dia]
        if isinstance(valor_columna_in, datetime):
            valor_columna_in = valor_columna_in.strftime('%H:%M:%S')
        # Obtener la posición de la columna actual en el DataFrame
        posicion_columna_in = horarios_df.columns.get_loc(columna_in)
        
        # Obtener el nombre de la columna a la derecha
        columna_out = horarios_df.columns[posicion_columna_in + 1] if posicion_columna_in < len(horarios_df.columns) - 1 else None
        valor_columna_out = row[columna_out] if columna_out is not None else None
        if isinstance(valor_columna_out, datetime):
            valor_columna_out = valor_columna_out.strftime('%H:%M:%S')
        
        if valor_columna_in != diaHorario.horaEntrada or valor_columna_out != diaHorario.horaSalida:
            print(f'Empleado: {empleado.nombreCompleto} - ID: {empleado.idEmpleado}')
            print(f'Horario Nuevo: {horario.id} - Dia: {dia} - In: {valor_columna_in} - Out: {valor_columna_out}')
            print(f'Horario viejo: {horario.id} - Dia: {dia} - In: {diaHorario.horaEntrada} - Out: {diaHorario.horaSalida}')
            return True
    return False
def leerPlanillaHorarios(horarioExcel):
    if horarioExcel:
        horarios_df = pd.read_excel(horarioExcel)
        horarios_df = horarios_df.where(pd.notna(horarios_df), "vacio")
        for index, row in horarios_df.iloc[1:].iterrows():
            empleado = crearEmpleadoFila(row)
            if validarHorario(row, empleado,horarios_df) ==True:
                print('No es igual')
                crearHorarioFila(row,horarios_df,empleado)
def leerPlanillaMarcas(marcasExcel):

    if marcasExcel:
        # Lee el archivo Excel
        df = pd.read_excel(marcasExcel)
        marcasEmpleadoPorDia = parseMarcas(df)
        for x in marcasEmpleadoPorDia:
            empleado = crearEmpleadoFila(x)
            crearMarcaEmpleado(empleado,x)
        # Convierte el diccionario a una lista de diccionarios

def calcInformeEmpleado(empleado,fechaInicio,fechaFin,margenEntrada):
    marcas = Marca.objects.filter(empleado=empleado,fechaHora__range=[fechaInicio, fechaFin]).order_by('fechaHora')
    llegadasTarde = []
    retirosFueradeHora = []
    zona_horaria_argentina = timezone.get_default_timezone()  # O usa timezone.pytz.timezone('America/Argentina/Buenos_Aires')

    for marca in marcas:
        if marca.tipoMarca is not None and marca.diaHorario is not None:
            if marca.tipoMarca.nombre == 'In':
                fecha_entrada = datetime.combine(marca.fechaHora.date(), marca.diaHorario.horaEntrada)
                
                # Convertir fecha_entrada a objeto consciente de la zona horaria
                fecha_entrada_con_zona = timezone.make_aware(fecha_entrada, zona_horaria_argentina)

                # Sumar el margen directamente a la fecha y hora de entrada
                fechaHoraInHorario = fecha_entrada_con_zona + timedelta(minutes=margenEntrada.minute, seconds=margenEntrada.second)
                if (marca.fechaHora - timedelta(minutes=1)).replace(second=0) > fechaHoraInHorario:
                    diferencia_tiempo = marca.fechaHora - fechaHoraInHorario
                    marca.diferenciaFalta = diferencia_tiempo
                    llegadasTarde.append(marca)
            elif marca.tipoMarca.nombre == 'Out':
                fecha_salida = datetime.combine(marca.fechaHora.date(), marca.diaHorario.horaSalida)
                
                # Convertir fecha_entrada a objeto consciente de la zona horaria
                fecha_salida_con_zona = timezone.make_aware(fecha_salida, zona_horaria_argentina)

                # Sumar el margen directamente a la fecha y hora de entrada
                fechaHoraOutHorario = fecha_salida_con_zona + timedelta(minutes=margenEntrada.minute, seconds=margenEntrada.second)
                if (marca.fechaHora + timedelta(minutes= 1)).replace(second=0) < fechaHoraOutHorario:
                    diferencia_tiempo = marca.fechaHora - fechaHoraOutHorario
                    marca.diferenciaFal = diferencia_tiempo
                    retirosFueradeHora.append(marca)
    return llegadasTarde , retirosFueradeHora

def descargarInformeExcel(empleados):
    # Crear un nuevo libro de trabajo
    workbook = Workbook()
    archivo = f'attachment; filename=registro{datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}.xlsx'
    # Seleccionar la hoja activa
    sheet = workbook.active

    # Escribir datos en algunas celdas
    columnas = ['ID Empleado', 'Empleado', 'Fecha','In/Out','Horario','Marca','Diferencia']
    
    sheet.append(columnas)
    for data_row in empleados:
        for llegadaTarde in data_row.llegadasTarde:
            fila = [data_row.idEmpleado, data_row.nombreCompleto, llegadaTarde.fechaHora.strftime('%d/%m/%Y'),llegadaTarde.tipoMarca.nombre,llegadaTarde.diaHorario.horaEntrada.strftime('%H:%M:%S'),llegadaTarde.fechaHora.strftime('%H:%M:%S'),llegadaTarde.diferenciaFalta]
            sheet.append(fila)
        for retirosFueradeHora in data_row.retirosFueradeHora:
            fila = [data_row.idEmpleado, data_row.nombreCompleto, retirosFueradeHora.fechaHora.strftime('%d/%m/%Y'),retirosFueradeHora.tipoMarca.nombre,retirosFueradeHora.diaHorario.horaSalida.strftime('%H:%M:%S'),retirosFueradeHora.fechaHora.strftime('%H:%M:%S'),retirosFueradeHora.diferenciaFal]
            sheet.append(fila)

     # Ajustar el formato de las celdas para que se vean mejor
    for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row, min_col=1, max_col=sheet.max_column):
        for cell in row:
            cell.alignment = Alignment(horizontal='center')  # Alineación centrada

    # Aplicar autofiltros
    sheet.auto_filter.ref = sheet.dimensions

    # Crear una respuesta HTTP con el archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = archivo

    # Guardar el libro de trabajo en el flujo de respuesta
    workbook.save(response)

    return response
def generarInforme(form):
    fechaInicio = form.cleaned_data['fechaInicio']
    fechaFin = form.cleaned_data['fechaFin']
    minutos = form.cleaned_data['minutos'] or 0
    segundos = form.cleaned_data['segundos'] or 0

        # Crea un objeto timedelta con los valores proporcionados
    margenEntrada = time(0,minutos,segundos)
    selectAll = form.cleaned_data['selectAll']
    if selectAll == 'all':
        empleados = Empleado.objects.all()
    else:
        empleados = [Empleado.objects.get(idEmpleado=empleado) for empleado in form.cleaned_data['empleados']]
    for empleado in empleados:
        llegadasTarde, retirosFueradeHora = calcInformeEmpleado(empleado,fechaInicio,fechaFin,margenEntrada)
        empleado.llegadasTarde = llegadasTarde
        empleado.retirosFueradeHora = retirosFueradeHora
    return descargarInformeExcel(empleados)
