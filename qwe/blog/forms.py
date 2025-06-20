from django import forms
from .models import Record, PasswordGenerator,UserMessage, AdminResponse, Feedback
from django_select2.forms import Select2Widget


class RecordForm(forms.ModelForm):
    codeword = forms.CharField(
        max_length=100,
        label='Пароль шифрования*',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите кодовое слово'
        })
    )

    class Meta:
        model = Record
        fields = ['title', 'ljg', 'pas', 'link', 'com', 'codeword']
        labels = {
            'title': 'Название сайта*',
            'ljg': 'Логин*',
            'pas': 'Пароль*',
            'link': 'Ссылка на сайт',
            'com': 'Комментарий',
            'codeword': 'Дополнительный пароль*'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название сайта'}),
            'ljg': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя пользователя'}),
            'pas': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Введите ссылку на сайт'}),
            'com': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Добавьте комментарий'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})  
            field.label = f'<p class="article-title">{field.label}</p>' 


class PasswordGeneratorForm(forms.ModelForm):
    class Meta:
        model = PasswordGenerator
        fields = ['length', 'include_digits', 'include_uppercase', 'include_special']
        labels = {
            'length': "Длина пароля",
            'include_digits': "Включать цифры",
            'include_uppercase': "Включать заглавные буквы",
            'include_special': "Включать специальные символы",
        }
        widgets = {
            'length': forms.NumberInput(attrs={
                'min': 1,
                'max': 100,
                'class': 'form-control',  
                'include_digits': forms.CheckboxInput(attrs={'class': 'form-check-input', 'placeholder': 'Длина пароля'}),
            }),

            'include_digits': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_uppercase': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_special': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['title', 'content']
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите отзыв'})
        }

class UserMessageForm(forms.ModelForm):
    class Meta:
        model = UserMessage
        fields = ['title', 'content']
        labels = {
            'title': 'Заголовок',
            'content': 'Содержание'
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите заголовок'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите сообщение'})
        }

class AdminResponseForm(forms.ModelForm):
    class Meta:
        model = AdminResponse
        fields = ['content']
        labels = {
            'content': 'Ответ'
        }
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Введите сообщение'})

        }



class SearchForm(forms.Form):
    query = forms.CharField(label='Поиск', max_length=100)


class DecryptPasswordForm(forms.Form):
    codeword = forms.CharField(label='Кодовое слово', max_length=256)

