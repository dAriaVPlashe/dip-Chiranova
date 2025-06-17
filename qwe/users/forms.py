from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, UserProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit)
        profile = Profile(user=user)
        if commit:
            profile.save()
        return user


class ProfileForm(forms.ModelForm):
    temp_keyword = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Введите дополнительный пароль'}))

    class Meta:
        model = Profile
        fields = ['temp_keyword']
        labels = {'temp_keyword': 'Пароль шифрации'}


class CodewordChangeForm(forms.Form):
    new_codeword = forms.CharField(
        label='Новый пароль шифрования',
        widget=forms.PasswordInput,
        max_length=128,
        required=True
    )

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class MyPasswordResetForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'email']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")

        if username and email:
            # Проверяем, существует ли пользователь с данным именем и электронной почтой
            if not User.objects.filter(username=username, email=email).exists():
                raise forms.ValidationError("Пользователь с таким именем и электронной почтой не найден.")

        return cleaned_data