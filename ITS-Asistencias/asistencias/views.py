from django.shortcuts import render

# Create your views here.


def mi_vista(request):
    return render(request, 'stats.html')
