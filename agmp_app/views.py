from django.shortcuts import render
from agmp_app.models import  *

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def resources(request):
    return render(request, 'resources.html')

def contact(request):
    return render(request, 'contact.html')