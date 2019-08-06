from django.shortcuts import render
from agmp_app.models import  *
from .forms import PostForm

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def search(request):
    form = PostForm(
        initial = {
            'gene_name': '',
            'protein': '',
            'function': ''
        }
    )
    return render(request, 'search.html', {"form": form})    

def resources(request):
    return render(request, 'resources.html')

def contact(request):
    return render(request, 'contact.html')