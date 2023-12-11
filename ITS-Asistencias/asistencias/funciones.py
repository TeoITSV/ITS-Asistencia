from datetime import datetime, timedelta,time
import json
import locale
from asistencias.models import *
from django.utils import timezone
import pandas as pd
from collections import defaultdict


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
            if x['ID de usuario'] == 117:
                crearMarcaEmpleado(empleado,x)
        # Convierte el diccionario a una lista de diccionarios



