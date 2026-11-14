from django.contrib import admin
from .models import (
    Categorie, Fournisseur, Produit, Lot, Client,
    Vente, LigneVente, MouvementStock,
)

admin.site.site_header = "Gestion Pharmacie - Administration"
admin.site.site_title = "Gestion Pharmacie"
admin.site.index_title = "Suivi de la pharmacie"


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone')
    search_fields = ('nom',)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('name', 'dosage', 'categorie', 'prix_vente',
                    'stock_total', 'statut_stock', 'sous_ordonnance', 'actif')
    list_filter = ('categorie', 'actif', 'sous_ordonnance')
    search_fields = ('name', 'dci', 'code_barres')


@admin.register(Lot)
class LotAdmin(admin.ModelAdmin):
    list_display = ('produit', 'numero_lot', 'date_expiration',
                    'quantite', 'prix_achat', 'fournisseur')
    list_filter = ('date_expiration', 'fournisseur')
    search_fields = ('produit__name', 'numero_lot')
    date_hierarchy = 'date_expiration'


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone')
    search_fields = ('nom', 'telephone')


class LigneVenteInline(admin.TabularInline):
    """Affiche les produits vendus directement dans la fiche de la vente."""
    model = LigneVente
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'vendeur', 'client', 'mode_paiement', 'total')
    list_filter = ('date', 'vendeur', 'mode_paiement')
    date_hierarchy = 'date'
    inlines = [LigneVenteInline]

    # Les ventes se font uniquement via la caisse de l'application.
    # Dans l'administration, le propriétaire peut les consulter
    # mais ni les créer, ni les modifier, ni les supprimer.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('date', 'lot', 'type', 'quantite', 'utilisateur', 'reference')
    list_filter = ('type', 'date', 'utilisateur')
    date_hierarchy = 'date'

    # Le journal de stock est un historique : il ne doit jamais être modifié à la main.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False