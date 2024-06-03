from datetime import datetime
from django import forms
from asistencias.models import Empleado
class UploadForm(forms.Form):
    horarios_file = forms.FileField(
        label='Archivo de Horarios (xlsx)',
        widget=forms.ClearableFileInput(attrs={'style': 'opacity: 0; position: absolute; z-index: -1;','id': 'horarios_file_input'},
        ),
        required=False
    )
    
    marcas_file = forms.FileField(
        label='Archivo de Marcas de Dedo (xlsx)',
        widget=forms.ClearableFileInput(attrs={'style': 'opacity: 0; position: absolute; z-index: -1;', 'id': 'marcas_file_input'}),
        required=False
    )

class InformeForm(forms.Form):
    OPCIONES_SELECCION = [
        ('all', 'Todos'),
        ('individual', 'Individuales'),
    ]
    fechaInicio = forms.DateField(
        label='Fecha Inicio',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'fechaInicio', 'required': True}),
        required=True
    )
    
    fechaFin = forms.DateField(
        label='Fecha Fin',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'fechaFin'}),
        required=True
    )
    empleados = forms.MultipleChoiceField(
        label='Empleados',
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'empleados','required':False}),
        required=False
    )
    selectAll = forms.ChoiceField(
        label='Seleccionar',
        choices=OPCIONES_SELECCION,
        widget=forms.Select(attrs={'class': 'form-control mb-2', 'id':'selectAll'}),
        required=True
    )

    minutos = forms.IntegerField(
        label='Minutos',
        widget=forms.NumberInput(attrs={'type': 'number', 'class': 'form-control', 'id': 'minutos', 'required': False}),
        required=False
    )
    
    segundos = forms.IntegerField(
        label='Segundos',
        widget=forms.NumberInput(attrs={'type': 'number', 'class': 'form-control', 'id': 'segundos', 'required': False}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super(InformeForm, self).__init__(*args, **kwargs)
        self.fields['empleados'].choices = [(empleado.idEmpleado, empleado.nombreCompleto) for empleado in Empleado.objects.filter(estaActivo=True)]
        today = datetime.today()
        first_day_of_month = today.replace(day=1)
        self.fields['fechaInicio'].initial = first_day_of_month.date()
        self.fields['fechaFin'].initial = today.date()
