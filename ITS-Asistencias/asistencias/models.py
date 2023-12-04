from django.db import models

# Create your models here.
class Base(models.Model):
    fechaCreacion = models.DateTimeField(auto_now_add=True);
    fechaModificacion = models.DateTimeField(auto_now=True);
    class Meta:
        abstract = True;
    def __str__(self):
        return str(self.id);
class Empleado(Base):
    idEmpleado = models.IntegerField(primary_key=True);
    nombreCompleto = models.CharField(max_length=100);
    estaActivo = models.BooleanField(default=True);
    
    def __str__(self):
        return self.nombreCompleto;
class Horario(Base):
    esActual = models.BooleanField(default=True);
    empleado = models.ForeignKey('Empleado', on_delete=models.CASCADE);
    fechaBajada = models.DateTimeField(null=True, blank=True);

    def __str__(self):
        return str(self.empleado.nombreCompleto);
class DiaHorario(Base):
    horaEntrada = models.TimeField(null=True, blank=True);
    horaSalida = models.TimeField(null=True, blank=True);
    diaNombre = models.ForeignKey('Dia', on_delete=models.CASCADE);
    horario = models.ForeignKey('Horario', on_delete=models.CASCADE);

class Dia(Base):
    nombre = models.CharField(max_length=10);
    def __str__(self):
        return self.nombre;
class TipoMarca(Base):
    nombre = models.CharField(max_length=10);
    descripcion = models.CharField(max_length=100);
class Marca(Base):
    fechaHora = models.DateTimeField();
    empleado = models.ForeignKey('Empleado', on_delete=models.CASCADE);
    tipoMarca = models.ForeignKey('TipoMarca', on_delete=models.CASCADE,null=True, blank=True);
    diaHorario = models.ForeignKey('DiaHorario', on_delete=models.CASCADE,null=True, blank=True);

