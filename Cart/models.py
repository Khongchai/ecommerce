import uuid

from django.db import models
from django.db.models.fields import related
from django.db.models.fields.related import ForeignKey
from django.conf import settings


# A cart is assigned automatically to both a logged-in and not-logged-in users
# Focus on logged-in users first
class Cart(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="carts")
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)

    def __str__(self):
        """
            If cart is complete, display: {user}-complete-{transaction-id} 
            else, display: {user}-current
        """
        return f"{self.customer.username}-complete-{self.transaction_id}" if self.complete else f"{self.customer.username}-current"

