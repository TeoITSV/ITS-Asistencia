from django.contrib import admin
from .models import Empleado, Horario, DiaHorario, Dia, TipoMarca, Marca

class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ('idEmpleado', 'nombreCompleto', 'estaActivo');
    search_fields = ('idEmpleado', 'nombreCompleto');
    list_filter = ('estaActivo',);

class HorarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'esActual', 'empleado');
    search_fields = ('id', 'empleado__nombreCompleto');
    list_filter = ('esActual', 'empleado__estaActivo');

class DiaHorarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'horaEntrada', 'horaSalida', 'diaNombre', 'horario');
    search_fields = ('id', 'diaNombre__nombre', 'horario__id');
    list_filter = ('diaNombre__nombre', 'horario__id');

class DiaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre');
    search_fields = ('id', 'nombre');

class TipoMarcaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion');
    search_fields = ('id', 'nombre', 'descripcion');

class MarcaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fechaHora', 'empleado', 'tipoMarca', 'diaHorario');
    search_fields = ('id', 'fechaHora', 'empleado__nombreCompleto', 'tipoMarca__nombre', 'diaHorario__id');
    list_filter = ('empleado__nombreCompleto', 'tipoMarca__nombre', 'diaHorario__id');

admin.site.register(Empleado, EmpleadoAdmin);
admin.site.register(Horario, HorarioAdmin);
admin.site.register(DiaHorario, DiaHorarioAdmin);
admin.site.register(Dia, DiaAdmin);
admin.site.register(TipoMarca, TipoMarcaAdmin);
admin.site.register(Marca, MarcaAdmin);


# Register your models here.
