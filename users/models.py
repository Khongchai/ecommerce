from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    email = models.EmailField(blank=False, max_length=254, verbose_name="email address")
    is_student = models.BooleanField(default=False)
    school_or_university = models.CharField(max_length=100, null=True, blank=True)

    USERNAME_FIELD = "username"   
    EMAIL_FIELD = "email"      

    def __str__(self):
        return self.username