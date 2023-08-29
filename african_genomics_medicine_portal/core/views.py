from django.shortcuts import render
from core.models import Journal, Author, Category
# Create your views here.

def BootstrapFilterView(request):

    qs = Journal.objects.all()

    title_cotains_query = request.GET.get('title_contains')
    title_exact_query = request.GET.get('title_exact')
    title_or_author_query = request.GET.get('title_or_author')

    if title_cotains_query != '' and title_cotains_query is not None:

        qs = qs.filter(title__icontains=title_cotains_query)


    context ={

        'queryset':qs
    }
    return render(request, "bootstrap_form.html",context)