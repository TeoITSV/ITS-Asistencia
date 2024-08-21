from django.db import models
from django.core.files.base import ContentFile
import string
import random
from PIL import Image, ImageDraw, ImageFont
import io
import os
from django.conf import settings
# Create your models here.
class Base(models.Model):
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    fechaModificacion = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True
    def __str__(self):
        return str(self.id)
class Empleado(Base):
    idEmpleado = models.IntegerField(primary_key=True)
    nombreCompleto = models.CharField(max_length=100)
    estaActivo = models.BooleanField(default=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    def getNombre(self):
        '''Capitaliza las primeras letras del nombre y apellido'''
        return string.capwords(self.nombreCompleto)
    def __str__(self):
        return f'{self.getNombre()}'
    def save(self, *args, **kwargs):
        if not self.profile_picture:
            self.profile_picture = self.generate_profile_picture()
        super().save(*args, **kwargs)

    def generate_profile_picture(self):
        # Generar un color de fondo aleatorio
        def random_color():
            return "#{:06x}".format(random.randint(0, 0xFFFFFF))

        # Obtener iniciales del nombre
        def get_initials(name):
            return ''.join([word[0].upper() for word in name.split()][:2])

        initials = get_initials(self.nombreCompleto)
        bg_color = random_color()
        font_size = 80
        img_width = 200
        img_height = 200
        image_size = (img_width, img_height)

        # Crear imagen
        image = Image.new('RGB', image_size, bg_color)
        draw = ImageDraw.Draw(image)

        # Ruta a la fuente
        font_path = os.path.join(settings.BASE_DIR, 'static/fonts', 'PoetsenOne-Regular.ttf')

        # Cargar fuente
        try:
            font = ImageFont.truetype(font_path, font_size)
        except OSError:
            raise OSError(f"Cannot open font resource at {font_path}")

        # Dibujar texto
        draw.text((img_width/2,img_height/2), initials, font=font, fill=(255, 255, 255),anchor="mm",align="center")

        # Guardar imagen en un objeto BytesIO
        image_io = io.BytesIO()
        image.save(image_io, format='PNG')
        image_content = ContentFile(image_io.getvalue(), f"{self.idEmpleado}_{self.nombreCompleto}_profile_picture.png")

        return image_content
class Horario(Base):
    esActual = models.BooleanField(default=True)
    empleado = models.ForeignKey('Empleado', on_delete=models.CASCADE)
    fechaBajada = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return str(self.empleado.nombreCompleto) + " " + str(self.id) + " " + self.fechaCreacion.strftime("%d/%m/%Y %H:%M:%S")
class DiaHorario(Base):
    horaEntrada = models.TimeField(null=True, blank=True)
    horaSalida = models.TimeField(null=True, blank=True)
    diaNombre = models.ForeignKey('Dia', on_delete=models.CASCADE)
    horario = models.ForeignKey('Horario', on_delete=models.CASCADE)
    def __str__(self):
        return str(self.diaNombre) + " In: " + str(self.horaEntrada)+ " Out: " + str(self.horaSalida)

class Dia(Base):
    nombre = models.CharField(max_length=10)
    def __str__(self):
        return self.nombre
class TipoMarca(Base):
    nombre = models.CharField(max_length=10)
    descripcion = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre
class Marca(Base):
    fechaHora = models.DateTimeField()
    empleado = models.ForeignKey('Empleado', on_delete=models.CASCADE)
    tipoMarca = models.ForeignKey('TipoMarca', on_delete=models.CASCADE,null=True, blank=True)
    diaHorario = models.ForeignKey('DiaHorario', on_delete=models.CASCADE,null=True, blank=True)
    def __str__(self):
        return str(self.empleado.nombreCompleto) + " " + str(self.fechaHora) + " " + str(self.tipoMarca)
class TipoFalta(Base):
    nombre = models.CharField(max_length=300)
    descripcion = models.TextField(max_length=300)
    def __str__(self):
        return self.nombre
class Falta(Base):
    marca = models.ForeignKey('Marca', on_delete=models.CASCADE, null=True, blank=True)
    empleado = models.ForeignKey('Empleado', on_delete=models.CASCADE , null=True, blank=True)
    tipoFalta = models.ForeignKey('TipoFalta', on_delete=models.CASCADE , null=True, blank=True)
    fechaHora = models.DateTimeField(null=True, blank=True)
    descripcion = models.TextField(max_length=300, null=True, blank=True)
    estaJustificada = models.BooleanField(default=False, null=True, blank=True)
    justificacion = models.TextField(max_length=300, null=True, blank=True)
    docs = models.FileField(upload_to='docs/', null=True, blank=True)
    def __str__(self):
        return str(self.empleado.nombreCompleto) + " " + str(self.tipoFalta) + " " + str(self.fechaCreacion)
