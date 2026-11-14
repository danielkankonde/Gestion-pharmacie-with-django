from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from datetime import datetime
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from .forms import AjoutProduit, AjoutVente 
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import timedelta
from django.db.models import Sum, F, Q, DecimalField, ExpressionWrapper
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, F, DecimalField, ExpressionWrapper
from .models import LigneVente
from .models import (
    Produit,
    Categorie,
    Client,
    Vente,
    Lot,
)


@login_required(login_url='login')
def dashboard(request):

    aujourd_hui = timezone.localdate()
    dans_30_jours = aujourd_hui + timedelta(days=30)

    # ==========================================
    # 1. STATISTIQUES GENERALES
    # ==========================================

    total_produits = Produit.objects.filter(actif=True).count()

    total_categories = Categorie.objects.count()

    total_clients = Client.objects.count()

    # ==========================================
    # 2. STATISTIQUES DES VENTES
    # ==========================================

    ventes_du_jour = Vente.objects.filter(
        date__date=aujourd_hui
    )

    total_ventes_jour = ventes_du_jour.count()

    chiffre_affaires_jour = ventes_du_jour.aggregate(
        total=Sum('total')
    )['total'] or 0

    # Chiffre d'affaires global
    chiffre_affaires_total = Vente.objects.aggregate(
        total=Sum('total')
    )['total'] or 0

    # ==========================================
    # 3. STATISTIQUES DU STOCK
    # ==========================================

    produits_stock = Produit.objects.filter(actif=True).annotate(
        stock_actuel=Sum(
            'lots__quantite',
            filter=Q(lots__date_expiration__gte=aujourd_hui)
        )
    )

    produits_rupture = produits_stock.filter(
        Q(stock_actuel=0) | Q(stock_actuel__isnull=True)
    ).count()

    produits_stock_bas = produits_stock.filter(
        stock_actuel__gt=0,
        stock_actuel__lte=F('seuil_alerte')
    ).count()

    # Quantité totale disponible
    stock_total = Lot.objects.filter(
        date_expiration__gte=aujourd_hui
    ).aggregate(
        total=Sum('quantite')
    )['total'] or 0

    # Valeur du stock au prix d'achat
    valeur_stock = Lot.objects.filter(
        date_expiration__gte=aujourd_hui
    ).aggregate(
        total=Sum(
            ExpressionWrapper(
                F('quantite') * F('prix_achat'),
                output_field=DecimalField(max_digits=20, decimal_places=2)
            )
        )
    )['total'] or 0

    # ==========================================
    # 4. LOTS QUI EXPIRENT BIENTOT
    # ==========================================

    lots_expiration = Lot.objects.filter(
        date_expiration__gte=aujourd_hui,
        date_expiration__lte=dans_30_jours,
        quantite__gt=0
    ).select_related('produit').order_by('date_expiration')

    # ==========================================
    # 5. DERNIERES VENTES
    # ==========================================

    dernieres_ventes = Vente.objects.select_related(
        'client',
        'vendeur'
    ).order_by('-date')[:5]

    # ==========================================
    # 7. TOP 5 DES MEDICAMENTS LES PLUS VENDUS
    # ==========================================

    top_medicaments = LigneVente.objects.values(
        'produit_id',
        'produit__name',
        'produit__dosage'
    ).annotate(
        quantite_vendue=Sum('quantite'),

        chiffre_affaires=Sum(
            ExpressionWrapper(
                F('quantite') * F('prix_unitaire'),
                output_field=DecimalField(
                    max_digits=20,
                    decimal_places=2
                )
            )
        )

    ).order_by('-quantite_vendue', '-chiffre_affaires')[:5]

    # ==========================================
    # 6. DONNEES ENVOYEES AU TEMPLATE
    # ==========================================

    context = {
        'total_produits': total_produits,
        'total_categories': total_categories,
        'total_clients': total_clients,

        'total_ventes_jour': total_ventes_jour,
        'chiffre_affaires_jour': chiffre_affaires_jour,
        'chiffre_affaires_total': chiffre_affaires_total,

        'produits_rupture': produits_rupture,
        'produits_stock_bas': produits_stock_bas,
        'stock_total': stock_total,
        'valeur_stock': valeur_stock,

        'lots_expiration': lots_expiration,
        'dernieres_ventes': dernieres_ventes,
        'top_medicaments': top_medicaments,

        'top_medicaments': top_medicaments,
    }

    return render(request, "dashboard.html", context)


class ListeProduits(LoginRequiredMixin, ListView):
#   # utilisation  du templates
    template_name = 'liste_produits.html'
#   # récupération du produit dans la base de données
    queryset = Produit.objects.all()


class AjoutProduit(LoginRequiredMixin, CreateView):
    # utilisation du modèle
    model = Produit
    # spécifier le formulaire à utiliser
    form_class = AjoutProduit
    # affichage du templates
    template_name = 'ajout_produit.html'
    #rediriger vers la page d'accueil
    success_url = reverse_lazy('home')
    
    
class modifier(LoginRequiredMixin, UpdateView):
    #utilisation du modèle
    model = Produit
    #spécifier le formulaire utiliser
    form_class = AjoutProduit
    #affichage du templates
    template_name = 'modifier.html'
    #rediriger vers la page d'accueil
    success_url = reverse_lazy('home')

@login_required(login_url='login')
def delete(request, id):
    if request == "POST":
        produit = get_object_or_404(Produit, id=id)
        produit.delete()
        return JsonResponse({'success': True, 'message':"Le produit à été supprimer avec succès"})
    return JsonResponse({'success': False, 'message': "Methode non autorisée"})

class detail(LoginRequiredMixin, DetailView):
    model = Produit
    template_name = 'detail.html' 


@login_required(login_url='login')
def search(request):
    query = request.GET.get('produit')
    donnees = Produit.objects.filter(name__icontains=query)
    return render(request, 'search.html', {'donnees': donnees})


#fonction pour la vente 
def VenteProduits(request, id):
    produit = get_object_or_404(Produit, id=id)
    message = None

    if request.method == "POST":
        form = AjoutVente(request.POST)

        if form.is_valid():
            quantite = form.cleaned_data["quantite"]
            customer = form.cleaned_data["customer"]

            if quantite > produit.quantite:
                messages.error(request, "la quantité demandée est supérieure à votre stock")
            
            else:
                customer, _ =Client.objects.get_or_create(name = customer)
                total_amount = produit.price * quantite

                #créer la vente avec l'instance Customer 
                sale = Vente(produit = produit, quantite= quantite, total_amount=total_amount, customer=customer)
                sale.save()

                produit.quantite -= quantite
                produit.save()

                return redirect('creer_facture', sale_id = sale.id)
        else:
            messages.error(request, "Formulaire invalide !")
    else:
        form = AjoutVente()
        
        if produit.quantite <= 5 and not message:
            message = "Attention, stock est trop bas !"
    return render(request, 'formulaire-vente.html', {'produit': produit, 'form':form, 'message':message})

#fonction pour le récu
def saverecu(request, id):
    vente = get_object_or_404(Vente, id=id)

    facture = Facture_client(
        produit = vente.produit,
        customer = vente.customer,
        quantite = vente.quantite,
        total_amount = vente.total_amount,
        sale_date = vente.sale_date
    )

    facture.save()
    message = "Réçu enregistré avec succès pour la vente {}".format(id)
    return redirect("creer_facture", sale_id = id)

#fonction pour la facture
def facture(request, sale_id):
    sale = get_object_or_404(Vente, id = sale_id)
    # facture = get_object_or_404(Facture_client, id = sale_id)
    # customer = get_object_or_404(Customer, id = sale_id)
    # message = "Réçu enregistré avec succès pour la vente {}".format(sale_id)

    context = {
        'produit': sale.produit.name,
        'customer': sale.customer,
        'quantite': sale.quantite,
        'total_amount': sale.total_amount,
        'sale': sale.id,
        'price': sale.produit.price,
        'date_achat': sale.sale_date
    }
    return render(request, 'facture-client.html', context)


# Create your views here.
# def home(request):
#     # appel des données depuis la base de données
#     object_list = Produit.objects.all()

#     ctx = {
#         'produits': object_list
#     }
#     return render(request, "home.html", ctx)

# def detail(request, id):

#     produit = Produit.objects.get(id=id)

#     return render(request, 'detail.html', {'produit':produit})

# def update(request, id):
#     produit = get_object_or_404(Produit, id=id)
#     categories = Categorie.objects.all()
#     errors = {}

#     if request.method == 'POST':
#         name = request.POST.get("name")
#         categorie_id = request.POST.get("category")
#         price = request.POST.get("price")
#         quantite = request.POST.get("quantite")
#         description = request.POST.get("description")
#         date_expiration = request.POST.get("date-expiration")
#         image = request.POST.get("image")

#         if not name:
#             errors['name'] = "le nom du produit est requis"
        
#         if not categorie_id:
#             errors['category'] = "la categorie du produit est réquise"

#         if not price:
#             errors['price'] = "la prix du produit est réquis"

#         if not quantite:
#             errors['quantite'] = "la quantité du produit est réquise"

#         if not description:
#             errors['description'] = "Entrez la description du produit"

#         if date_expiration:
#             try:
#                 date_expiration = datetime.strptime(date_expiration, '%Y-%m-%d')
#             except:
#                 errors['date-expiration'] = "le format de la date est incorrect, utilisez le format %AAAA-%MM-%JJ"
        
#         if not errors:
#             category = get_object_or_404(Categorie, id=categorie_id)
#             produit.name = name
#             produit.categorie = category
#             produit.price = price
#             produit.quantite = quantite
#             produit.description = description
#             produit.date_expiration = date_expiration

#             if image:
#                     filestorage = FileSystemStorage()
#                     filename = filestorage.save(name.name, image)
#                     produit.image = filestorage.url(filename)

#         produit.save()
#         messages.success(request, 'produit enregistrer avec succès')
#         return redirect('home')

#     else:
#         for key, errror in errors.items():
#             messages.error(request, errror)

#     return render(request, "modification.html", {'produit': produit,'categorie':categories, 'errors':errors})


            
# def ajout_produit(request):
#     # declaration d'une variable qui va gérer les erreurs
    errors = {}
    if request.method == 'POST':
        name = request.POST["name"]
        price = request.POST["price"]
        quantite = request.POST["quantite"]
        description = request.POST["description"]
        date_expiration = request.POST["date-expiration"]
        image = request.FILES["image"]

        try:
            date_expiration = datetime.strptime(date_expiration, '%Y-%m-%a')
        except:
            errors['date_expiration'] = 'le format de la date est incorrect, utilisez le format %AAAA-%YY-%JJ'
        
        try:
            price = float(price)
            if price < 0:
                errors['price'] = 'le price ne doit pas étre négative '
        except ValueError:
            errors['price'] = 'Entrez un prix valide !'

        if not errors:
            try:
                # récupération des catégories dans la table en fonction de la clé primaire
                categorie = Categorie.objects.get(pk=request.POST['category'])
                savedonnes = Produit(name=name, price=price, quantite=quantite, description=description, date_expiration=date_expiration, image = image, categorie = categorie)
                savedonnes.save()
                messages.success(request, 'le produit à été ajouter avec succès')
            except Categorie.DoesNotExist:
                errors['category'] = f'la categorie spécifiée est introuvable'
            except KeyError as e:
                errors[str(e)] = f'le champs {e} est manquant dans la requete'
            except Exception as e:
                messages.error(request,f'une erreur est survenue: {e}')
            return redirect('home')  
    else:
        categorie = Categorie.objects.all
    return render(request, "ajout_produit.html", {'category': categorie, 'errors':errors})
