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
    # A composition can have many movments. The data for the movements can live on separate locations.
    composition = models.ForeignKey(Composition, on_delete=models.CASCADE,  null=True, blank=True, related_name="links")

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
    # free = false means free for only students
    # free = true means free for everyone
    free = models.BooleanField(default=False)

    def __str__(self):
        call_this = self.composition.name if self.composition else "Not yet assigned to a composition"
        return call_this


 

# class Cart(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
#     date_ordered = models.DateTimeField(auto_now_add=True)
#     complete = models.BooleanField(default=False)
#     transaction_id = models.CharField(max_length=100, null=True)
    
#     def __str__(self):
#         return str(self.id)

    # @property
    # def get_cart_total(self):
    #     itemsincart = self.itemincart_set.all()
    #     total = sum([item.get_total for item in itemsincart])
    #     return total

    # @property
    # def get_cart_items(self):
    #     itemsincart = self.itemincart_set.all()
    #     total = sum([item.quantity for item in itemsincart])
    #     return total

# class ItemInCart(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
#     cart =  models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True)
#     quantity = models.IntegerField(default=0, null=True, blank=True)
#     date_added = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.product.name
    
#     @property 
#     def get_total(self):
#         total = self.product.price * self.quantity
#         return total