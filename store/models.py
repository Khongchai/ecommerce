from Cart.models import Cart
from users.models import CustomUser
from django.db import models

# Add fixtures in the order the models are added.

class Composer(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Composition(models.Model):
    name = models.CharField(max_length=200)
    # A composer can compose many pieces and a piece can be composed by more than 1 composer.
    composers = models.ManyToManyField(Composer , related_name="compositions")

    def __str__(self):
        return self.name


class DataAfterPurchase(models.Model):
    midi_link = models.URLField(max_length = 500, blank=True, null=True)
    wav_link = models.URLField(max_length = 500, blank=True, null=True)
    flac_link = models.URLField(max_length = 500, blank=True, null=True)
    pdf_link = models.URLField(max_length = 500, blank=True, null=True)

    """
        In previous version, all movements are linked to one composition,
        now, each movement gets its own composition model, eg. Mozart Piano Concert No.21 2nd mvt 
    """
    composition = models.OneToOneField(Composition, on_delete=models.CASCADE,  null=True, blank=True, related_name="links")
    purchased_by = models.ManyToManyField(CustomUser, related_name="purchased_items")
    

    @property
    def name(self):
        return f"data for {self.composition.name}"

    def __str__(self):
       return f"{self.composition.name}"


class Product(models.Model):
    price_usd = models.DecimalField(max_digits=7, decimal_places=2)
    image_link = models.URLField(max_length = 500)
    # when this field is deleted, set the authenticated_data field of Product to null
    composition = models.OneToOneField(Composition , on_delete=models.SET_NULL, null=True, blank=True, related_name="product")
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name="items_in_cart")

    def __str__(self):
        call_this = self.composition.name if self.composition else "Not yet assigned to a composition"
        return call_this
