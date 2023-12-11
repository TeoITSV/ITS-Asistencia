from django import forms
from asistencias.models import Empleado
class UploadForm(forms.Form):
    horarios_file = forms.FileField(
        label='Archivo de Horarios (xlsx)',
        widget=forms.ClearableFileInput(attrs={'style': 'opacity: 0; position: absolute; z-index: -1;','id': 'horarios_file_input'}),
    )
    
    marcas_file = forms.FileField(
        label='Archivo de Marcas de Dedo (xlsx)',
        widget=forms.ClearableFileInput(attrs={'style': 'opacity: 0; position: absolute; z-index: -1;', 'id': 'marcas_file_input'}),
        required=True
    )

class InformeForm(forms.Form):
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
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'id': 'empleados'}),
        required=True
    )
    margenEntrada = forms.TimeField(
        label='Margen Entrada',
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'id': 'margenEntrada', 'required': True}),
        required=True
    )
    def __init__(self, *args, **kwargs):
        super(InformeForm, self).__init__(*args, **kwargs)
        self.fields['empleados'].choices = [(empleado.idEmpleado, empleado.nombreCompleto) for empleado in Empleado.objects.filter(estaActivo=True)]
        self.fields['empleados'].initial = [empleado.idEmpleado for empleado in Empleado.objects.filter(estaActivo=True)]
        self.fields['empleados'].widget.attrs['size'] = len(self.fields['empleados'].choices)
        self.fields['empleados'].widget.attrs['style'] = 'height: auto;'
        self.fields['empleados'].widget.attrs['required'] = True
        self.fields['empleados'].widget.attrs['multiple'] = True
        self.fields['empleados'].widget.attrs['data-live-search'] = True
        self.fields['empleados'].widget.attrs['data-none-results-text'] = 'No se encontraron resultados'
        self.fields['empleados'].widget.attrs['data-none-selected-text'] = 'Seleccione uno o más empleados'
        self.fields['empleados'].widget.attrs['data-selected-text-format'] = 'count > 3'
        self.fields['empleados'].widget.attrs['data-count-selected-text'] = 'Seleccionados {0} de {1}'
        self.fields['empleados'].widget.attrs['data-actions-box'] = True
        self.fields['empleados'].widget.attrs['data-deselect-all-text'] = 'Deseleccionar todo'
        self.fields['empleados'].widget.attrs['data-select-all-text'] = 'Seleccionar todo'
        self.fields['empleados'].widget.attrs['data-style'] = 'btn-outline-secondary'
