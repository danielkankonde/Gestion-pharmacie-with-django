from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect


def est_dernier_proprietaire(user):
    """Vrai si `user` est le seul propriétaire actif de l'application."""
    User = get_user_model()
    return not (
        User.objects.filter(is_superuser=True, is_active=True)
        .exclude(pk=user.pk)
        .exists()
    )


class ProprietaireRequisMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Pour les vues basées sur des classes : accès réservé au propriétaire."""

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        # Utilisateur connecté mais pas propriétaire : message + retour à l'accueil
        if self.request.user.is_authenticated:
            messages.error(self.request, "Cette page est réservée au propriétaire.")
            return redirect("acc")
        # Utilisateur non connecté : redirection vers la page de connexion
        return super().handle_no_permission()


def proprietaire_requis(vue):
    """Pour les vues fonctions : accès réservé au propriétaire."""

    @login_required
    @wraps(vue)
    def enveloppe(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, "Cette action est réservée au propriétaire.")
            return redirect("acc")
        return vue(request, *args, **kwargs)

    return enveloppe
