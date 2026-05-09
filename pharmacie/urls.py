from django.urls import path
from .views import *

urlpatterns = [
    path('', acc, name="acc"),
    path('home', affichage.as_view(), name="home"),
    path('ajout/',  AjoutProduits.as_view(), name="ajout_produit"),
    path('modifier/<int:pk>/',  modifier.as_view(), name="modifier"),
    path('supprimer/<int:id>/', delete, name="supprimer"),
    path('detail/<int:pk>/', detail.as_view(), name="detail"),
    path('recherche/', search, name="recherche"),
    path('ajoutvente/<int:id>/', VenteProduits, name="ajoutvente"),
    path('enregistrement-recu/<int:id>/', saverecu, name="saverecu"),
    path('creer_facture/<int:sale_id>/', facture, name="creer_facture"),

    
    # path('', home, name='home'),
    # path('ajout/', ajout_produit, name="ajout_produit"),
    # path('modification/<int:id>/', update, name="modifier"),
]