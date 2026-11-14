from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.functional import cached_property
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, FormView, ListView, UpdateView

from .forms import (
    ChangerMotDePasseForm,
    ConnexionForm,
    ReinitMotDePasseForm,
    UtilisateurCreationForm,
    UtilisateurModificationForm,
)
from .permissions import ProprietaireRequisMixin, proprietaire_requis

User = get_user_model()


class Connexion(LoginView):
    """Page de connexion. Un utilisateur déjà connecté est renvoyé à l'accueil."""

    template_name = "utilisateurs/login.html"
    authentication_form = ConnexionForm
    redirect_authenticated_user = True


class ListeUtilisateurs(ProprietaireRequisMixin, ListView):
    model = User
    template_name = "utilisateurs/liste.html"
    context_object_name = "utilisateurs"
    ordering = ["-is_active", "-is_superuser", "first_name", "username"]


class CreerUtilisateur(ProprietaireRequisMixin, SuccessMessageMixin, CreateView):
    form_class = UtilisateurCreationForm
    template_name = "utilisateurs/formulaire.html"
    success_url = reverse_lazy("utilisateurs_liste")
    success_message = "Le compte « %(username)s » a été créé."
    extra_context = {
        "titre": "Nouvel utilisateur",
        "sous_titre": "Créez un compte pour une personne qui utilisera l’application.",
        "bouton": "Créer le compte",
        "retour": reverse_lazy("utilisateurs_liste"),
    }


class ModifierUtilisateur(ProprietaireRequisMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UtilisateurModificationForm
    template_name = "utilisateurs/formulaire.html"
    success_url = reverse_lazy("utilisateurs_liste")
    success_message = "Le compte « %(username)s » a été mis à jour."

    def get_context_data(self, **kwargs):
        contexte = super().get_context_data(**kwargs)
        nom = self.object.get_full_name() or self.object.username
        contexte.update(
            titre=f"Modifier {nom}",
            bouton="Enregistrer",
            retour=reverse_lazy("utilisateurs_liste"),
        )
        return contexte


class ReinitialiserMotDePasse(ProprietaireRequisMixin, FormView):
    """Le propriétaire choisit un nouveau mot de passe pour un utilisateur."""

    form_class = ReinitMotDePasseForm
    template_name = "utilisateurs/formulaire.html"
    success_url = reverse_lazy("utilisateurs_liste")

    @cached_property
    def cible(self):
        return get_object_or_404(User, pk=self.kwargs["pk"])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.cible
        return kwargs

    def get_context_data(self, **kwargs):
        contexte = super().get_context_data(**kwargs)
        nom = self.cible.get_full_name() or self.cible.username
        contexte.update(
            titre=f"Nouveau mot de passe pour {nom}",
            sous_titre="Communiquez-lui ensuite ce mot de passe de vive voix.",
            bouton="Changer le mot de passe",
            retour=reverse_lazy("utilisateurs_liste"),
        )
        return contexte

    def form_valid(self, form):
        form.save()
        nom = self.cible.get_full_name() or self.cible.username
        messages.success(self.request, f"Le mot de passe de {nom} a été changé.")
        return super().form_valid(form)


@proprietaire_requis
@require_POST
def basculer_actif(request, pk):
    """Désactive ou réactive un compte (on ne supprime jamais : l'historique est conservé)."""
    cible = get_object_or_404(User, pk=pk)
    nom = cible.get_full_name() or cible.username

    if cible == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
    else:
        cible.is_active = not cible.is_active
        cible.save(update_fields=["is_active"])
        etat = "réactivé" if cible.is_active else "désactivé"
        messages.success(request, f"Le compte de {nom} a été {etat}.")
    return redirect("utilisateurs_liste")


class MonMotDePasse(LoginRequiredMixin, SuccessMessageMixin, PasswordChangeView):
    """Chaque utilisateur peut changer son propre mot de passe."""

    form_class = ChangerMotDePasseForm
    template_name = "utilisateurs/formulaire.html"
    success_url = reverse_lazy("acc")
    success_message = "Votre mot de passe a été modifié."
    extra_context = {
        "titre": "Changer mon mot de passe",
        "bouton": "Enregistrer",
        "retour": reverse_lazy("acc"),
    }
