from django import forms
from django.forms import ModelForm
from .models import Produit


class AjoutProduit(ModelForm):

    class Meta:
        model = Produit

        fields = [
            'name',
            'dci',
            'dosage',
            'forme',
            'categorie',
            'code_barres',
            'prix_vente',
            'seuil_alerte',
            'sous_ordonnance',
            'description',
            'image',
            'actif',
        ]

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex : Doliprane',
            }),

            'dci': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex : Paracétamol',
            }),

            'dosage': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex : 500 mg',
            }),

            'forme': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex : Comprimé, sirop, injectable...',
            }),

            'categorie': forms.Select(attrs={
                'class': 'form-select',
            }),

            'code_barres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Code-barres du médicament',
            }),

            'prix_vente': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Prix de vente',
                'step': '0.01',
                'min': '0',
            }),

            'seuil_alerte': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex : 10',
                'min': '0',
            }),

            'sous_ordonnance': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Description, indications et précautions...',
                'rows': 4,
            }),

            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),

            'actif': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

        labels = {
            'name': 'Nom commercial',
            'dci': 'DCI (molécule active)',
            'dosage': 'Dosage',
            'forme': 'Forme pharmaceutique',
            'categorie': 'Catégorie',
            'code_barres': 'Code-barres',
            'prix_vente': 'Prix de vente',
            'seuil_alerte': "Seuil d'alerte du stock",
            'sous_ordonnance': 'Médicament soumis à ordonnance',
            'description': 'Description',
            'image': 'Image du médicament',
            'actif': 'Médicament actif',
        }

# formulaire de vente

class AjoutVente(forms.Form):

    quantite = forms.IntegerField(
        min_value=1,
        help_text="Veuillez entrer la quantité à vendre",
        required=True,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Quantité à vendre',
            'class': 'form-control'
        })
    )

    client = forms.CharField(
        max_length=250,
        required=False,
        help_text="Nom du client (facultatif)",
        widget=forms.TextInput(attrs={
            'placeholder': 'Nom du client',
            'class': 'form-control'
        })
    )
