from django import forms

from .models import pharmacogenes,Product

class ModelSelectForm(forms.Form):
    MODELS = [
        ('product', 'Product'),
        # Add more models as needed
    ]

    model_choice = forms.ChoiceField(choices=MODELS, widget=forms.RadioSelect)
    search_query = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'id': 'autocomplete'}))



class PostForm(forms.ModelForm):
    class Meta:
        model = pharmacogenes
        # list fields
        fields = ('gene_name', 'function')
        error_css_class = 'error'
        required_css_class = 'bold'
        # https://www.webforefront.com/django/formtemplatelayout.html
        # TODO: allow empty fields
    


class SearchForm(forms.Form):
    SEARCH_CHOICES = (
        ('Variantagmp', 'Variant'),
        ('Geneagmp', 'Gene'),
        ('Drugagmp', 'Drug'),
        ('Disease', 'Disease'),
    )
    search_option = forms.ChoiceField(choices=SEARCH_CHOICES, widget=forms.RadioSelect,label="Choose a category to search by")
    search_query = forms.CharField(max_length=100)


class SearchFormNew(forms.Form):
    CHOICES = [('Variantagmp', 'Variantagmp'), ('Drugagmp', 'Drugagmp')]
    choice = forms.ChoiceField(choices=CHOICES)
    query = forms.CharField(widget=forms.TextInput(attrs={'class': 'autocomplete'}))
