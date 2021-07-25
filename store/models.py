from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=200)
    price_usd = models.DecimalField(max_digits=7, decimal_places=2)
    image_link = models.URLField(max_length = 200)
    authenticated_data = models.OneToOneField("DataAfterPurchase", on_delete=models.CASCADE,  null=True, blank=True, related_name="product")

    def __str__(self):
        return self.name

class DataAfterPurchase(models.Model):
    midi_link = models.URLField(max_length = 200)
    wav_link = models.URLField(max_length = 200)
    flac_link = models.URLField(max_length = 200)

    @property
    def name(self):
        try:
            product = self.product
            return product.name
        except:
            product = False 
            return f"data id {self.id} not yet linked to any product"

    def __str__(self):
       return f"{self.name}-data"

 

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