from django.urls import path
from .views import *

urlpatterns = [
    path('login/', connect_account, name="login"),
    path('creation/', create_account, name="creation"),
    path('verification', verificationEmail, name="verification"),
    path('modifierCode/<str:email>/', modifierCode, name="modifierCode"),
    path('deconnection/', deconnexion, name="deconnection"),
]