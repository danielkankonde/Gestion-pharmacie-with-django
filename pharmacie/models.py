from django.db import models

# Create your models here.
class Categorie(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name

class Produit(models.Model):
    name = models.CharField(max_length=250)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    price = models.IntegerField()
    quantite = models.PositiveIntegerField(default=0)
    description = models.TextField()
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateField()
    image = models.ImageField(upload_to='images/')
    def __str__(self):
        return self.name +' (' + str(self.categorie) +')'

    class Meta:
        ordering = ['-date_ajout']
    
    def get_image_url(self):
        if self.image:
            return self.image.url
        else:
            return None

    def statut_quantite(self):
        if self.quantite == 0:
            return 'red'
        elif self.quantite <= 10:
            return 'orange'
        else:
            return 'green'    
class Customer(models.Model):
    name = models.CharField(max_length=250)
    def __str__(self):
        return self.name
class Vente(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    sale_date = models.DateTimeField(auto_now_add=True)
    quantite = models.PositiveIntegerField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits= 10, decimal_places=2)

    def __str__(self):
        return self.produit + ' (' + str(self.quantite)+ ')'

class Facture_client(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    date_achat = models.DateTimeField(auto_now_add=False)
    total_amount = models.ForeignKey(Vente, on_delete=models.CASCADE)





            
