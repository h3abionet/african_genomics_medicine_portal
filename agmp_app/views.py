from django.shortcuts import render
from agmp_app.models import  *

# Create your views here.
def  overview(request):
    snps=snp.objects.all()
    drugs=drug.objects.all()
    genes=pharmacogenes.objects.all()
    studies=study.objects.all()
    return render(request, 'overview.html', 
            {'snps': snps,
            'drugs': drugs,
            'genes': genes,
            'studies': studies})
