from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import MyPasswordResetForm, UserProfileForm, ProfileForm, CodewordChangeForm
import hashlib
from .models import Profile

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('profile')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists():
                messages.success(request, f'Пользователь с таким email уже существует.')
            else:
                form.save()
                username = form.cleaned_data.get('username')
                messages.success(request, f'Ваш аккаунт создан: можно войти на сайт.')
                return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})



@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserProfileForm(request.POST, instance=request.user)
        if u_form.is_valid():
            new_email = u_form.cleaned_data.get('email')
            if User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
                messages.error(request, 'Пользователь с таким email уже существует.')
            else:
                u_form.save()
                messages.success(request, 'Ваш профиль успешно обновлен.')
                return redirect('profile')
    else:
        u_form = UserProfileForm(instance=request.user)

    context = {
        'u_form': u_form,
    }
    return render(request, 'users/profile.html', context)


@login_required
def Change_permission(request, user_id):
    admin_profile = request.user.profile


    if not admin_profile.is_admin:
        messages.error(request, 'У вас нет прав для изменения разрешений.')
        return redirect('profile')

    target_profile = Profile.objects.get(user__id=user_id)

    if request.method == 'POST':
        target_profile.can_change_codeword = not target_profile.can_change_codeword
        target_profile.save()
        messages.success(request, f'Разрешение на изменение для {target_profile.user.username} изменено.')
        return redirect('user_list')

    return render(request, 'users/change_permission.html', {'profile': target_profile})


@login_required
def Change_codeword(request):
    profile = request.user.profile


    if not profile.can_change_codeword:
        messages.error(request, 'У вас нет прав для изменения пароля! Запросите права у администратора.')
        return redirect('profile')

    if request.method == 'POST':
        form = CodewordChangeForm(request.POST)
        if form.is_valid():
            new_codeword = form.cleaned_data['new_codeword']
            profile.hashed = new_codeword
            profile.can_change_codeword = False
            profile.save()
            messages.success(request, 'Пароль успешно изменен!')
            return redirect('profile')
    else:
        form = CodewordChangeForm()

    return render(request, 'users/change_codeword.html', {'form': form})

@login_required
def User_list(request):
    admin_profile = request.user.profile


    if not admin_profile.is_admin:
        messages.error(request, 'У вас нет прав для доступа к этому списку.')
        return redirect('profile')


    profiles = Profile.objects.all()
    return render(request, 'users/user_list.html', {'profiles': profiles})


class MyPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset.html'
    success_url = reverse_lazy('password_reset_done')
    form_class = MyPasswordResetForm

    def form_valid(self, form):
        return super().form_valid(form)


class MyPasswordResetDone(PasswordResetDoneView):
    template_name = 'users/password_reset_done_my.html'


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'users/password_reset_confirm_my.html'

class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete_my.html'
