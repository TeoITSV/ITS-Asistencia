import datetime
from asistencias.models import *
import pandas as pd
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
        horarioActual.fechaBajada = datetime.datetime.now()
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
        
        # Hacer algo con el valor de la columna a la derecha
        
        crearDiaHorario(horario,dia,valor_columna_in,valor_columna_out)
def validarHorario(horarios_df, empleado):
    # implementar logica en un futuro para evitar entradas duplicadas el mismo dia
    horarios = Horario.objects.filter(empleado=empleado,esActual=True)
    for horario in horarios:
        diasHorario = DiaHorario.objects.filter(horario=horario)
        for diaHorario in diasHorario:
            return True
            
def leerPlanillaHorarios(horarioExcel):
    if horarioExcel:
        horarios_df = pd.read_excel(horarioExcel)
        horarios_df = horarios_df.where(pd.notna(horarios_df), "vacio")
        for index, row in horarios_df.iloc[1:].iterrows():
            empleado = crearEmpleadoFila(row)
            crearHorarioFila(row,horarios_df,empleado)
