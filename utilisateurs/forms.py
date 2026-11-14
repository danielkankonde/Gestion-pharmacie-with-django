from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    SetPasswordForm,
    UserCreationForm,
)

from .permissions import est_dernier_proprietaire

User = get_user_model()

ROLES = [
    ("vendeur", "Vendeur / Vendeuse"),
    ("proprietaire", "Propriétaire"),
]

AIDE_ROLE = (
    "Le propriétaire a accès à tout. "
    "Le vendeur n’a accès qu’à la caisse et aux produits."
)


def appliquer_role(user, role):
    """Le propriétaire est superutilisateur ; le vendeur n'a aucun privilège spécial."""
    est_proprietaire = role == "proprietaire"
    user.is_superuser = est_proprietaire
    user.is_staff = est_proprietaire


class StyleMixin:
    """Ajoute la classe CSS 'champ' à tous les champs du formulaire."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for champ in self.fields.values():
            champ.widget.attrs.setdefault("class", "champ")


class ConnexionForm(StyleMixin, AuthenticationForm):
    error_messages = {
        "invalid_login": "Identifiant ou mot de passe incorrect.",
        "inactive": "Ce compte est désactivé. Contactez le propriétaire.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Identifiant"
        self.fields["username"].widget.attrs.update(
            {"placeholder": "Votre identifiant", "autocomplete": "username"}
        )
        self.fields["password"].label = "Mot de passe"
        self.fields["password"].widget.attrs.update(
            {"placeholder": "Votre mot de passe", "autocomplete": "current-password"}
        )


class UtilisateurCreationForm(StyleMixin, UserCreationForm):
    role = forms.ChoiceField(
        label="Rôle", choices=ROLES, initial="vendeur", help_text=AIDE_ROLE
    )

    field_order = [
        "first_name", "last_name", "username", "role", "password1", "password2",
    ]

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "last_name", "username")
        labels = {
            "first_name": "Prénom",
            "last_name": "Nom",
            "username": "Identifiant de connexion",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["password1"].label = "Mot de passe"
        self.fields["password2"].label = "Confirmer le mot de passe"

    def save(self, commit=True):
        user = super().save(commit=False)
        appliquer_role(user, self.cleaned_data["role"])
        if commit:
            user.save()
        return user


class UtilisateurModificationForm(StyleMixin, forms.ModelForm):
    role = forms.ChoiceField(label="Rôle", choices=ROLES, help_text=AIDE_ROLE)

    field_order = ["first_name", "last_name", "username", "role"]

    class Meta:
        model = User
        fields = ("first_name", "last_name", "username")
        labels = {
            "first_name": "Prénom",
            "last_name": "Nom",
            "username": "Identifiant de connexion",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["first_name"].required = True
        self.fields["role"].initial = (
            "proprietaire" if self.instance.is_superuser else "vendeur"
        )

    def clean_role(self):
        role = self.cleaned_data["role"]
        if (
            self.instance.pk
            and self.instance.is_superuser
            and role != "proprietaire"
            and est_dernier_proprietaire(self.instance)
        ):
            raise forms.ValidationError(
                "Impossible : c’est le dernier propriétaire actif de l’application."
            )
        return role

    def save(self, commit=True):
        user = super().save(commit=False)
        appliquer_role(user, self.cleaned_data["role"])
        if commit:
            user.save()
        return user


class ReinitMotDePasseForm(StyleMixin, SetPasswordForm):
    """Le propriétaire définit un nouveau mot de passe pour un utilisateur."""


class ChangerMotDePasseForm(StyleMixin, PasswordChangeForm):
    """Un utilisateur change son propre mot de passe."""
