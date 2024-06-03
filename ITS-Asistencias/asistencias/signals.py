from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Dia, TipoMarca


@receiver(post_migrate)
def verificar_dias(sender, **kwargs):
    dias_en_espanol = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    if Dia.objects.count() == 0:
        for dia in dias_en_espanol:
            Dia.objects.create(nombre = dia)

@receiver(post_migrate)
def verificar_tipos_marca(sender, **kwargs):
    tiposMarca = ['In','Out']
    if TipoMarca.objects.count() == 0:
        for tipo in tiposMarca:
            TipoMarca.objects.create(nombre = tipo, descripcion = 'Autogenerada')
