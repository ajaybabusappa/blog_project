from django.db import models

# Create your models here.

class UserModel(models.Model):
    class Roles(models.TextChoices):
        USER = "user"
        ADMIN = "admin"

    username = models.CharField(max_length=150, unique=True, primary_key=True)
    fullname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.USER)