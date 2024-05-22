from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Dia


@receiver(post_migrate)
def verificar_y_crear_datos(sender, **kwargs):
    dias_en_espanol = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    if Dia.objects.count() == 0:
        for dia in dias_en_espanol:
            Dia.objects.create(nombre = dia)
