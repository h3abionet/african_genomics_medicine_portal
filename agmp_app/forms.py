from django import forms

from .models import pharmacogenes

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


class ModelSearchForm(forms.Form):


    MODELS_CHOICES = [
        ('variantagmp', 'Variantagmp'),
        ('geneagmp', 'Geneagmp'),
        ('drugagmp', 'Drugagmp'),
        ('disease', 'Disease'),
    ]

    model_selection = forms.ChoiceField(choices=MODELS_CHOICES, widget=forms.RadioSelect,label="Choose a category to search by")
    search_query = forms.CharField(max_length=100, required=False)


