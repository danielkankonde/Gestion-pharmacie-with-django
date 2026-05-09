from django.forms import ModelForm
from django import forms
from .models import Produit, Categorie




class AjoutProduit(ModelForm):

    class Meta:
        model = Produit
        fields = [
            'name','categorie', 'price','quantite', 'description','date_expiration','image'
        ]
        error_messages = {
            'date_expiration': {
                'required': 'la date_expiration est obligatoire',
                'invalid':"Veuillez entrer une date valide au format AAAA/MM/jj",
            }
        }
        widget = {
            'name': forms.TextInput(
                attrs={
                    'placeholder':'le nom du produit',
                    'class':'form-control',
                }
            ),
            'categorie': forms.Select(
                attrs={
                    'class':'form-control'
                }
            ),
            'price': forms.NumberInput(
                attrs={
                    'placeholder':'Entrez le prix du produit',
                    'class':'form-control'
                }
            ),
            'quantite': forms.NumberInput(
                attrs={
                    'placeholder':'Entrez le quantité du produit',
                    'class':'form-control'
                }
            ),
            'description': forms.Textarea(
                attrs={
                    'placeholder':'description',
                    'class':'form-control',
                    'row': 4
                }
            ),
            'date_expiration': forms.TextInput(
                attrs={
                    'placeholder':'date-expiration',
                    'class': 'form-control',
                    
                }
            ),
            'image': forms.FileInput(
                attrs={
                    'class':'form-control-file'
                }
            )
            
        }
        
        def __init__(self, *args, **kwargs):
            
            super(AjoutProduit, self).__init__(*args, **kwargs)

            self.fields['name'].error_messages = {
                'required': 'le nom est obligatoire',
                'invalid': 'veuillez renseigner un nom valide'
            }
            self.fields['categorie'].error_messages = {
                'required': 'le categorie est obligatoire',
                'invalid': 'veuillez sélectionner une catégorie valide'
            }
            self.fields['price'].error_messages = {
                'required': 'le price est obligatoire',
                'invalid': 'veuillez entrez un prix valide'
            }
            self.fields['quantite'].error_messages = {
                'required': 'la quantité est obligatoire',
                'invalid': 'veuillez entrez une quantité valide'
            }
            self.fields['description'].error_messages = {
                'required': 'la description est obligatoire',
                'invalid': 'veuillez entrez une description valide'
            }
            # self.fields['date_expiration'].error_messages = {
            #     'required': 'la date_expiration est obligatoire',
            #     'invalid': 'veuillez entrez une date valide'
            # }

# formulaire de vente
class AjoutVente(forms.ModelForm):
    quantite = forms.IntegerField(
        help_text='Veuillez entrer la quantité du produit',
        required=True
    )
    customer = forms.CharField(
        help_text='Veuillez entrer le nom du client',
        required=True,
        max_length=100
    )

    class Meta:
        model = Produit
        fields = ['quantite','customer']

        widgets = {
            'customer':forms.TextInput(
                attrs={
                    'placeholder':"Le nom du produit",
                    'class':"forms-control"
                }
            ),
            'quantite':forms.NumberInput(
                attrs={
                    'placeholder':"la quantite du produit",
                    'class':"forms-control"
                }
            )
        }
