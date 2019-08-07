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

def search_details(request, db_name, query_id):
    '''
    Receive query parameters from search page to fetch
    database specific results
    '''
    return render(
        request, 'search_details.html', {
            'db_name': db_name,
            'query_id': query_id
            }
        )

def resources(request):
    return render(request, 'resources.html')

def contact(request):
    return render(request, 'contact.html')