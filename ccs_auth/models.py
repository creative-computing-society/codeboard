from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import CUserManager

class CUser(AbstractBaseUser):
    id = models.CharField(max_length=100, unique=True, blank=True)
    email = models.EmailField(unique=True, blank=False, null=False, primary_key=True)
    roll_no = models.CharField(max_length=10, unique=False, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    branch = models.CharField(max_length=50, blank=True, null=True, unique=False)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CUserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email
    
    def has_perm(self, perm, obj=None):
        return self.is_admin
    
    def has_module_perms(self, app_label):
        return True
