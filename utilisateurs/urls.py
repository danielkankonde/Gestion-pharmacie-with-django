from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    Connexion,
    CreerUtilisateur,
    ListeUtilisateurs,
    ModifierUtilisateur,
    MonMotDePasse,
    ReinitialiserMotDePasse,
    basculer_actif,
)

urlpatterns = [
    # Connexion / déconnexion
    path("login/", Connexion.as_view(), name="login"),
    path("deconnection/", LogoutView.as_view(), name="deconnection"),
    # Pour tout utilisateur connecté
    path("mot-de-passe/", MonMotDePasse.as_view(), name="mot_de_passe"),
    # Réservé au propriétaire
    path("utilisateurs/", ListeUtilisateurs.as_view(), name="utilisateurs_liste"),
    path("utilisateurs/nouveau/", CreerUtilisateur.as_view(), name="utilisateur_creer"),
    path("utilisateurs/<int:pk>/modifier/", ModifierUtilisateur.as_view(), name="utilisateur_modifier"),
    path("utilisateurs/<int:pk>/mot-de-passe/", ReinitialiserMotDePasse.as_view(), name="utilisateur_motdepasse"),
    path("utilisateurs/<int:pk>/activer/", basculer_actif, name="utilisateur_basculer"),
]
