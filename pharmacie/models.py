from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils import timezone


# =====================================================================
# CATÉGORIE : sert à classer les produits (Antibiotiques, Antalgiques...)
# =====================================================================
class Categorie(models.Model):
    # Nom de la catégorie. "unique=True" empêche de créer deux fois la même.
    name = models.CharField("Nom", max_length=250, unique=True)

    class Meta:
        verbose_name = "Catégorie"      # nom affiché dans l'administration
        ordering = ['name']             # tri alphabétique par défaut

    def __str__(self):
        return self.name


# =====================================================================
# FOURNISSEUR : l'entreprise ou la personne qui vous vend les médicaments
# =====================================================================
class Fournisseur(models.Model):
    # Nom du fournisseur (grossiste, laboratoire...)
    nom = models.CharField(max_length=250)
    # Numéro pour le joindre. "blank=True" = champ facultatif.
    telephone = models.CharField(max_length=30, blank=True)
    # Adresse du fournisseur (facultatif)
    adresse = models.TextField(blank=True)

    def __str__(self):
        return self.nom


# =====================================================================
# PRODUIT : la "fiche" d'un médicament (ses caractéristiques générales).
# Attention : le produit ne contient PAS la quantité en stock.
# Le stock est géré dans les LOTS (voir plus bas).
# =====================================================================
class Produit(models.Model):
    # Nom commercial tel qu'écrit sur la boîte (ex: Doliprane)
    name = models.CharField("Nom commercial", max_length=250)
    # DCI = Dénomination Commune Internationale, c'est-à-dire la molécule
    # active (ex: Paracétamol). Utile pour proposer un équivalent
    # quand un médicament est en rupture.
    dci = models.CharField("DCI (molécule)", max_length=250, blank=True)
    # Dosage du médicament (ex: 500 mg)
    dosage = models.CharField(max_length=100, blank=True)
    # Forme du médicament (comprimé, sirop, injectable, pommade...)
    forme = models.CharField(max_length=100, blank=True)
    # Catégorie du produit. "PROTECT" = on ne peut pas supprimer une
    # catégorie tant qu'elle contient des produits (évite de tout perdre).
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT)
    # Code-barres de la boîte, pour pouvoir scanner plus tard.
    # "db_index=True" rend la recherche par code-barres très rapide.
    code_barres = models.CharField(max_length=50, blank=True, db_index=True)
    # Prix auquel on vend le produit au client (avec centimes possibles)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2)
    # Quand le stock total tombe à ce nombre ou moins, l'application
    # signale "stock bas" pour penser à recommander.
    seuil_alerte = models.PositiveIntegerField(default=10)
    # Cocher si le médicament ne peut être vendu que sur ordonnance
    sous_ordonnance = models.BooleanField(default=False)
    # Notes libres : indications, précautions, conservation...
    description = models.TextField(blank=True)
    # Photo de la boîte (facultatif)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)
    # Au lieu de supprimer un produit qu'on ne vend plus, on le désactive.
    # Ainsi l'historique des anciennes ventes reste intact.
    actif = models.BooleanField(default=True)
    # Date de création de la fiche, remplie automatiquement
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} {self.dosage}".strip()

    # Stock total = somme des quantités de tous les lots NON périmés.
    # Ce n'est pas un champ enregistré : c'est calculé à chaque fois,
    # donc il est toujours juste.
    @property
    def stock_total(self):
        total = self.lots.filter(
            date_expiration__gte=timezone.localdate()
        ).aggregate(t=Sum('quantite'))['t']
        return total or 0

    # Donne l'état du stock : 'rupture' (0), 'bas' (sous le seuil) ou 'ok'.
    # Sert à afficher des couleurs (rouge / orange / vert).
    @property
    def statut_stock(self):
        if self.stock_total == 0:
            return 'rupture'
        if self.stock_total <= self.seuil_alerte:
            return 'bas'
        return 'ok'


# =====================================================================
# LOT : un arrivage précis d'un produit.
# Exemple : vous recevez 100 boîtes de Doliprane qui expirent en 2027,
# puis plus tard 50 boîtes qui expirent en 2028. Ce sont 2 lots.
# C'est indispensable car chaque lot a sa propre date de péremption.
# =====================================================================
class Lot(models.Model):
    # À quel produit appartient ce lot. "related_name='lots'" permet
    # d'écrire produit.lots pour retrouver tous les lots d'un produit.
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, related_name='lots')
    # Numéro de lot imprimé sur la boîte (important pour la traçabilité :
    # en cas de rappel d'un médicament, on sait qui l'a acheté)
    numero_lot = models.CharField(max_length=100)
    # Date de péremption de ce lot
    date_expiration = models.DateField()
    # Quantité ENCORE disponible dans ce lot. Elle diminue à chaque vente.
    quantite = models.PositiveIntegerField(default=0)
    # Prix auquel vous avez ACHETÉ ce lot (sert à calculer votre bénéfice)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # Qui vous a vendu ce lot. "SET_NULL" = si on supprime le fournisseur,
    # le lot reste, simplement sans fournisseur.
    fournisseur = models.ForeignKey(Fournisseur, null=True, blank=True,
                                    on_delete=models.SET_NULL)
    # Date à laquelle vous avez reçu le lot (aujourd'hui par défaut)
    date_reception = models.DateField(default=timezone.localdate)

    class Meta:
        # Tri par date de péremption : le lot qui expire en premier est en tête.
        # On vend toujours celui-là d'abord (règle FEFO : "premier expiré,
        # premier sorti") pour éviter les pertes.
        ordering = ['date_expiration']

    def __str__(self):
        return f"{self.produit} - lot {self.numero_lot}"


# =====================================================================
# CLIENT : la personne qui achète (facultatif à la vente)
# =====================================================================
class Client(models.Model):
    # Nom du client
    nom = models.CharField(max_length=250)
    # Téléphone du client (facultatif)
    telephone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.nom


# =====================================================================
# VENTE : l'"en-tête" d'un passage en caisse.
# Une vente = un client qui paie. Elle peut contenir plusieurs produits
# (ces produits sont dans LigneVente, juste après).
# =====================================================================
class Vente(models.Model):
    # Liste des modes de paiement possibles : (valeur enregistrée, texte affiché)
    MODES = [('cash', 'Espèces'), ('mobile', 'Mobile money'), ('carte', 'Carte')]

    # Le client (facultatif : en pharmacie beaucoup d'achats sont anonymes).
    # Si le client est supprimé, la vente reste.
    client = models.ForeignKey(Client, null=True, blank=True, on_delete=models.SET_NULL)
    # L'utilisateur connecté qui a fait la vente. Permet au propriétaire de
    # savoir QUI a vendu quoi. On ne peut pas supprimer un utilisateur
    # qui a déjà fait des ventes.
    vendeur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    # Date et heure de la vente, enregistrées automatiquement
    date = models.DateTimeField(auto_now_add=True)
    # Comment le client a payé
    mode_paiement = models.CharField(max_length=10, choices=MODES, default='cash')
    # Montant total à payer = somme des lignes de la vente
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ['-date']   # les ventes les plus récentes en premier

    def __str__(self):
        return f"Vente n°{self.pk} - {self.date:%d/%m/%Y}"


# =====================================================================
# LIGNE DE VENTE : un produit à l'intérieur d'une vente.
# Exemple : une vente avec Paracétamol x2 et Amoxicilline x1
# contient 2 lignes. C'est ce qui permet de vendre plusieurs
# médicaments dans la même facture.
# =====================================================================
class LigneVente(models.Model):
    # La vente à laquelle appartient cette ligne. "CASCADE" = si la vente
    # est supprimée, ses lignes le sont aussi.
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='lignes')
    # Le produit vendu
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT)
    # Le lot dans lequel on a pris les boîtes (pour la traçabilité)
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT)
    # Combien de boîtes/unités ont été vendues
    quantite = models.PositiveIntegerField()
    # Prix d'UNE unité AU MOMENT de la vente. On le recopie ici pour que
    # les anciennes factures ne changent pas si le prix évolue plus tard.
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    # Total de la ligne = quantité x prix unitaire (calculé, non enregistré)
    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire


# =====================================================================
# MOUVEMENT DE STOCK : le "journal" de tout ce qui entre et sort.
# Chaque fois que le stock change, une ligne est ajoutée ici.
# C'est l'historique qui permet de contrôler et de retrouver
# l'origine d'un écart de stock.
# =====================================================================
class MouvementStock(models.Model):
    # Les raisons possibles d'un changement de stock
    TYPES = [('entree', 'Entrée'), ('vente', 'Vente'),
            ('ajustement', 'Ajustement'), ('perte', 'Perte / périmé')
        ]

    # Le lot concerné par le mouvement
    lot = models.ForeignKey(Lot, on_delete=models.PROTECT, related_name='mouvements')
    # La raison : arrivage, vente, correction d'inventaire, perte/péremption
    type = models.CharField(max_length=12, choices=TYPES)
    # Quantité du mouvement : positive si ça entre (+50), négative si ça sort (-2)
    quantite = models.IntegerField()
    # Date et heure du mouvement, automatiques
    date = models.DateTimeField(auto_now_add=True)
    # Qui a effectué l'opération (pour savoir qui a modifié le stock)
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    # Texte libre pour retrouver l'origine (ex: "Vente n°45", "Inventaire du 30/11")
    reference = models.CharField(max_length=100, blank=True)