from django import forms

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
