from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def resources(request):
    return render(request, 'resources.html')

def contact(request):
    return render(request, 'contact.html')
