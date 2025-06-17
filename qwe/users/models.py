from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
import hashlib


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    hashed = models.CharField(max_length=128, default='')
    can_change_codeword = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.hashed:
            self.hashed = hashlib.sha256(self.hashed.encode()).hexdigest()
        super().save(*args, **kwargs)

    def check_codeword(self, codeword):
        hashed_codeword = hashlib.sha256(codeword.encode()).hexdigest()
        return self.hashed == hashed_codeword

    def __str__(self):
        return f'{self.user.username} Profile'


class UserProfile(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField()