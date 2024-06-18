from django import forms



class ModelSelectForm(forms.Form):
    MODELS = [
        ('product', 'Product'),
        # Add more models as needed
    ]

    model_choice = forms.ChoiceField(choices=MODELS, widget=forms.RadioSelect)
    search_query = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'id': 'autocomplete'}))





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
        ('variantagmp', 'Variant'),
        ('geneagmp', 'Gene'),
        ('drugagmp', 'Drug'),
        ('disease', 'Disease'),
    ]

    model_selection = forms.ChoiceField(choices=MODELS_CHOICES, widget=forms.RadioSelect,label="Choose a category to search by")
    search_query = forms.CharField(max_length=100, required=False, label="Search")


