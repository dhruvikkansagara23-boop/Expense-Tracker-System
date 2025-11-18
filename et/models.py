
from django.db import models
from django.contrib.auth.models import AbstractUser

# from .validator import validate_email_format, validate_strong_password
from .validator.email_validator import validate_email_format
from .validator.password_validator import validate_strong_password


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
  
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(unique=True, validators=[validate_email_format])
    password = models.CharField(max_length=255, validators=[validate_strong_password])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email or self.username
    
    
from django.conf import settings
from django.db import models

class Category(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Expense(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} - ₹{self.amount}"
