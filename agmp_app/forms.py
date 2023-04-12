from django import forms

from .models import pharmacogenes, CountryData
# Define the models to be searched
from .models import Variantagmp, Drugagmp, Geneagmp



class PostForm(forms.ModelForm):
    class Meta:
        model = pharmacogenes
        # list fields
        fields = ('gene_name', 'function')
        error_css_class = 'error'
        required_css_class = 'bold'
        # https://www.webforefront.com/django/formtemplatelayout.html
        # TODO: allow empty fields
    
class CountryDataFrom(forms.ModelForm):
    class Meta:
        model = CountryData
        fields = '__all__'

class SearchForm(forms.Form):
    SEARCH_CHOICES = (
        ('Variantagmp', 'Variant'),
        ('Geneagmp', 'Gene'),
        ('Drugagmp', 'Drug'),
    )
    search_option = forms.ChoiceField(choices=SEARCH_CHOICES, widget=forms.RadioSelect)
    search_query = forms.CharField(max_length=100)