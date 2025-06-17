from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib import messages

@receiver(user_logged_in)
def prompt_set_codeword(sender, request, user, **kwargs):
    profile = getattr(user, 'profile', None)
    if profile and profile.hashed == '':
        messages.info(request, 'Пожалуйста, задайте дополнительный пароль.')
