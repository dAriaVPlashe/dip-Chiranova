from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from cryptography.fernet import Fernet
from users.models import Profile
import base64
import hashlib

class Record(models.Model):
    title = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    ljg = models.CharField(max_length=1000)  
    pas = models.CharField(max_length=1000) 
    link = models.CharField(max_length=1000, default='', blank=True)
    date_posted = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    com = models.TextField(max_length=1000, default='Вы можете добавить комментарий', blank=True)

    def encrypt_password(self, password, codeword):
        hashed_codeword = hashlib.sha256(codeword.encode()).digest()
        fernet = Fernet(base64.urlsafe_b64encode(hashed_codeword))
        return fernet.encrypt(password.encode()).decode()

    def decrypt_password(self, encrypted_password, codeword):
        hashed_codeword = hashlib.sha256(codeword.encode()).digest()
        fernet = Fernet(base64.urlsafe_b64encode(hashed_codeword))
        return fernet.decrypt(encrypted_password.encode()).decode()

    def save(self, *args, **kwargs):
        profile = Profile.objects.get(user=self.author)
        codeword = profile.hashed

        # Если пароль не зашифрован, шифруем его перед сохранением
        if self.pas and not self.pas.startswith('gAAAA'):
            self.pas = self.encrypt_password(self.pas, codeword)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('record-detail', kwargs={'pk': self.pk})

    def get_decrypted_password(self):
        profile = Profile.objects.get(user=self.author)
        codeword = profile.hashed
        return self.decrypt_password(self.pas, codeword)




class PasswordGenerator(models.Model):
    length = models.PositiveIntegerField(default=12)
    include_digits = models.BooleanField(default=True)
    include_uppercase = models.BooleanField(default=True)
    include_special = models.BooleanField(default=True)

    def __str__(self):
        return f"PasswordGenerator(length={self.length}, include_digits={self.include_digits}, include_uppercase={self.include_uppercase}, include_special={self.include_special})"


class Feedback(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('user_feedback_detail', kwargs={'feedback_id': self.id})


class UserMessage(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_responded = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('user_message_detail', kwargs={'message_id': self.id})


class AdminResponse(models.Model):
    message = models.ForeignKey(UserMessage, related_name='responses', on_delete=models.CASCADE)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Response to {self.message.title} by {self.admin.username}'
