import json
from django.http import HttpResponseForbidden
from cryptography.fernet import InvalidToken
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from .forms import RecordForm, PasswordGeneratorForm
from django.http import JsonResponse
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from .models import Record, UserMessage, AdminResponse,Feedback
from cryptography.fernet import Fernet
import string
import random
from .forms import UserMessageForm, AdminResponseForm, FeedbackForm
from django.urls import reverse_lazy
from django.urls import reverse
from django.template.loader import render_to_string
from users.models import Profile


class UserMessageCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = UserMessageForm()
        return render(request, 'blog/create.html', {'form': form})

    def post(self, request):
        form = UserMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.save()
            return redirect('user_message_list')
        return render(request, 'blog/create.html', {'form': form})


class RecordDeleteMessage(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = UserMessage
    template_name = 'blog/delete_message.html'
    success_url = reverse_lazy('user_message_list')

    def test_func(self):
        message = self.get_object()
        return self.request.user == message.author

    def get_object(self, queryset=None):
        message_id = self.kwargs.get('message_id')
        return self.get_queryset().get(id=message_id)


class UserMessageListView(LoginRequiredMixin, ListView):
    model = UserMessage
    template_name = 'blog/list.html'
    context_object_name = 'messages'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(author=self.request.user)


class UserMessageDetailView(LoginRequiredMixin, View):
    def get(self, request, message_id):
        message = get_object_or_404(UserMessage, id=message_id)
        responses = message.responses.all()
        response_form = AdminResponseForm()
        return render(request, 'blog/detail.html', {
            'message': message,
            'responses': responses,
            'response_form': response_form
        })

    def post(self, request, message_id):
        message = get_object_or_404(UserMessage, id=message_id)
        response_form = AdminResponseForm(request.POST)
        if response_form.is_valid():
            response = response_form.save(commit=False)
            response.message = message
            response.admin = request.user
            response.save()
            message.is_responded = True
            message.save()
            return redirect('user_message_detail', message_id=message.id)
        responses = message.responses.all()
        return render(request, 'blog/detail.html', {
            'message': message,
            'responses': responses,
            'response_form': response_form
        })



def Delete_response(request, response_id):

    response = get_object_or_404(AdminResponse, id=response_id)
    message_id = response.message.id

    if request.method == 'POST':
        response.delete()  # Удаляем ответ
        return redirect('user_message_detail', message_id=message_id)

    return redirect('user_message_detail', message_id=message_id)


class UserMessageUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = UserMessage
    form_class = UserMessageForm
    template_name = 'blog/update_message.html'  #

    def get_object(self, queryset=None):
        message_id = self.kwargs.get('message_id')
        return self.get_queryset().get(id=message_id)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def test_func(self):
        message = self.get_object()
        return self.request.user == message.author

def home(request):
    context = {
        'records': Record.objects.all()
    }
    return render(request, 'blog/hi_home.html', context)

def generate_password(length, include_digits=True, include_uppercase=True, include_special=True):
    characters = string.ascii_lowercase
    if include_digits:
        characters += string.digits
    if include_uppercase:
        characters += string.ascii_uppercase
    if include_special:
        characters += string.punctuation

    return ''.join(random.choice(characters) for _ in range(length))

def generate_password_view(request):
    password = None
    if request.method == 'POST':
        form = PasswordGeneratorForm(request.POST)
        if form.is_valid():
            length = form.cleaned_data['length']
            include_digits = form.cleaned_data['include_digits']
            include_uppercase = form.cleaned_data['include_uppercase']
            include_special = form.cleaned_data['include_special']
            password = generate_password(length, include_digits, include_uppercase, include_special)
    else:
        form = PasswordGeneratorForm()

    return render(request, 'blog/generate_password.html', {'form': form, 'password': password})


class RecordListView(ListView):
    model = Record
    template_name = 'blog/home.html'
    context_object_name = 'records'
    paginate_by = 5

    def get_queryset(self):
        user = self.request.user
        return Record.objects.filter(author=user).order_by('-date_posted')


def serch_record(request):
    paginate_by = 5
    query = request.GET.get('query') if request.GET.get('query') is not None else ''
    records = Record.objects.filter(title__icontains=query)
    return render(request, 'blog/record_list.html',{'records': records})



class RecordDetailView(DetailView):
    model = Record


class RecordCreateView(LoginRequiredMixin, CreateView):
    model = Record
    form_class = RecordForm
    success_url = reverse_lazy('p_home')

    def dispatch(self, request, *args, **kwargs):
        profile = getattr(request.user, 'profile', None)
        if profile is None or not profile.hashed:
            messages.error(request, 'Пожалуйста, задайте дополнительный пароль в профиле перед созданием записи.')
            return redirect('profile')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        profile = getattr(self.request.user, 'profile', None)
        entered_codeword = form.cleaned_data.get('codeword')
        if not entered_codeword:
            form.add_error('codeword', 'Кодовое слово обязательно.')
            return self.form_invalid(form)

        if not profile.check_codeword(entered_codeword):
            messages.error(self.request, 'Кодовое слово неверно.')
            return self.form_invalid(form)


        raw_password = form.cleaned_data.get('pas')
        try:
            encrypted_password = form.instance.encrypt_password(raw_password, profile.hashed)
            form.instance.pas = encrypted_password
        except ValueError as e:
            form.add_error('pas', 'Ошибка шифрования пароля: ' + str(e))
            return self.form_invalid(form)

        form.instance.author = self.request.user
        return super().form_valid(form)


class RecordCreatePsView(LoginRequiredMixin, CreateView):
    model = Record
    form_class = RecordForm
    success_url = reverse_lazy('p_home')

    def dispatch(self, request, *args, **kwargs):
        profile = getattr(request.user, 'profile', None)
        if profile is None or not profile.hashed:
            messages.error(request, 'Пожалуйста, задайте дополнительный пароль в профиле перед созданием записи.')
            return redirect('profile')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        profile = getattr(self.request.user, 'profile', None)

        entered_codeword = form.cleaned_data.get('codeword')
        if not entered_codeword:
            form.add_error('codeword', 'Дополнительный пароль обязателен для шифрования пароля')
            return self.form_invalid(form)

        if not profile.check_codeword(entered_codeword):
            messages.error(self.request, 'Кодовое слово неверно.')
            return self.form_invalid(form)

        raw_password = form.cleaned_data.get('pas')
        if not raw_password:
            form.add_error('pas', 'Пароль обязателен.')
            return self.form_invalid(form)

        try:
            encrypted_password = form.instance.encrypt_password(raw_password, profile.hashed)
            form.instance.pas = encrypted_password
        except ValueError as e:
            form.add_error('pas', 'Ошибка шифрования пароля: ' + str(e))
            return self.form_invalid(form)

        form.instance.author = self.request.user
        return super().form_valid(form)


class DecryptPasswordView(LoginRequiredMixin, View):
    def post(self, request, record_id):
        record = get_object_or_404(Record, id=record_id, author=request.user)

        try:
            data = json.loads(request.body)
            codeword_input = data.get('codeword')

            if not codeword_input:
                return JsonResponse({'error_message': 'Кодовое слово не передано'}, status=400)

            # Получаем профиль пользователя
            profile = getattr(request.user, 'profile', None)
            if profile is None or profile.hashed == '':
                return JsonResponse({'error_message': 'Пожалуйста, задайте дополнительный пароль в профиле.'}, status=400)


            if not profile.check_codeword(codeword_input):
                return JsonResponse({'error_message': 'Кодовое слово неверно.'}, status=403)
            decrypted_password = record.get_decrypted_password()

            return JsonResponse({'decrypted_password': decrypted_password})

        except json.JSONDecodeError:
            return JsonResponse({'error_message': 'Неверный формат JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error_message': 'Ошибка при расшифровке'}, status=500)



class RecordUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Record
    form_class = RecordForm

    def get_initial(self):
        initial = super().get_initial()
        record = self.get_object()


        try:
            decrypted_password = record.get_decrypted_password()
            initial['pas'] = decrypted_password
        except Exception:
            initial['pas'] = ''

        return initial

    def form_valid(self, form):

        profile = getattr(self.request.user, 'profile', None)

        if profile is None or profile.hashed == '':
            messages.error(self.request, 'Пожалуйста, задайте дополнительный пароль в профиле.')
            return redirect('profile')

        codeword = form.cleaned_data.get('codeword') or self.request.POST.get('codeword')
        if not codeword:
            form.add_error('codeword', 'Дополнительный пароль обязателен для шифрования пароля')
            return self.form_invalid(form)

        if not profile.check_codeword(codeword):
            messages.error(self.request, 'Кодовое слово неверно.')
            return self.form_invalid(form)

        raw_password = form.cleaned_data['pas']
        try:
            encrypted_password = form.instance.encrypt_password(raw_password, profile.hashed)
            form.instance.pas = encrypted_password  #
        except ValueError as e:
            form.add_error('pas', 'Ошибка шифрования пароля: ' + str(e))
            return self.form_invalid(form)

        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        record = self.get_object()
        return self.request.user == record.author




class RecordDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Record
    success_url = reverse_lazy('p_home')

    def test_func(self):
        record = self.get_object()
        if self.request.user == record.author:
                return True
        return False



def feedback_create(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.author = request.user
            feedback.save()
            return redirect('user_feedback_detail', feedback_id=feedback.id)
    else:
        form = FeedbackForm()
    return render(request, 'blog/feedback_form.html', {'form': form})


def feedback_edit(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    if feedback.author != request.user:
        return HttpResponseForbidden("Вы не можете редактировать этот отзыв.")

    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=feedback)
        if form.is_valid():
            form.save()
            return redirect('user_feedback_detail', feedback_id=feedback.id)
    else:
        form = FeedbackForm(instance=feedback)

    return render(request, 'blog/feedback_form.html', {'form': form})



def feedback_delete(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    if feedback.author != request.user:
        return HttpResponseForbidden("Вы не можете удалять этот отзыв.")

    if request.method == 'POST':
        feedback.delete()
        messages.success(request, 'Отзыв успешно удалён.')
        return redirect('feedback_list')

    return render(request, 'blog/feedback_confirm_delete.html', {'feedback': feedback})


def feedback_detail(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    return render(request, 'blog/feedback_detail.html', {'feedback': feedback})


def feedback_list(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')
    return render(request, 'blog/feedback_list.html', {'feedbacks': feedbacks})

def home(request):
    feedbacks = Feedback.objects.all().order_by('-created_at')[:3]
    return render(request, 'blog/hi_home.html', {'feedbacks': feedbacks})


def about(request):
    return render(request, 'blog/about.html', {'title': 'О нас'})