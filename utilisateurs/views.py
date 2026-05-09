from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

import re
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


# Create your views here.
def create_account(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        password_confirm = request.POST["password-confirm"]

        if password != password_confirm:
            messages.error(request, "Les mots de passe ne sont identiques. Veuillez réessayer.")
            return redirect("creation")
        
        if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'\d',password) or not re.search(r'[!@a$%(),.?":{}|`<>]'):
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères, incluent des lettres, des chiffres et des caractères spéciaux")
            return redirect("creation")
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "L'addresse e-mail invalide, Veuillez réessayer. ")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom de l'utilisateur existe déjà, Veuillez réessayer.")
            return redirect("creation")
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Cette adresse e-mail est déjà utilisée. Veuillez en choisir une autre")
            return redirect("creation")
        
        User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Compte crée avec succès. Connectez-vous maintenant")
        return redirect("login")
    
    return render(request, "create_account.html")


def connect_account(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('acc')
        else:
            messages.error(request,"Le nom d'utilisateur ou mot de passe est incorrect")
            return redirect("login")
    return render(request, "login.html")

# fonction pour la verification email
def verificationEmail(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if not email:
            messages.error(request, "Veuillez rentrer un email valide !")
            return (request, "verification.html")
        
        user = User.objects.filter(email = email).first
        if user:
            return redirect("modifierCode", email = email)
        else:
            messages.error(request, "Nom d'utilisateur introuvable, veuillez reesayer ou créer un autre compte")
            return redirect("verification")
        
    return render(request, "verification.html")

# fonction pour modifier le mot de passe
def modifierCode(request, email):

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, "L'utilisateur est introuvable")
        return redirect("verification")
    
    if request.method == "POST":
        password = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if password == password_confirm:
            if len(password) < 8:
                messages.error(request, "Le mot de passe doit contenir au moins 8 caractères !")
            elif not any(char.isdigit() for char in password):
                messages.error("Le mot de passe doit contenir au moins un chiffre")
            elif not any(char.isalpha() for char in password):
                messages.error(request, "Le mot de passe doit conténir au moins une lettre")
            else:
                user.set_password(password)
                user.save()
                return redirect("login")
        else:
            messages.error(request, "Le mot de passe ne correspondent pas, Réessayer !")
        
    context = {
        'email': email,        
    }
    return render(request, "modificationCode.html", context)

# fonction pour se déconnecter
def deconnexion(request):

    logout(request)
    return redirect('login')



