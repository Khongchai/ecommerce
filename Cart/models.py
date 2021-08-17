import uuid

from django.db import models
from django.db.models.fields import related
from django.db.models.fields.related import ForeignKey
from django.conf import settings


# A cart is assigned automatically to both a logged-in and not-logged-in users
# Focus on logged-in users first
class Cart(models.Model):
    customer = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="cart")
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)

    def __str__(self):
        """
            If cart is complete, display: {user}-complete-{transaction-id} 
            else, display: {user}-current
        """
        return f"{self.customer.username}-complete-{self.transaction_id}" if self.complete else f"{self.customer.username}-current"


# Reference
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
