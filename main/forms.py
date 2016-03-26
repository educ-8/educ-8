from django import forms

class SearchForm(forms.Form):
    search_term = forms.CharField(label="",
      max_length=200,
      widget=forms.TextInput(
        attrs={
        'id': 'search-term', 'class': 'form-control', 'required': True, 'placeholder': 'Princeton University, Pomona College...'
        })
      )
