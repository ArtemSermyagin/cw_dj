import datetime
import json

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.contrib.auth.views import LoginView
from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.core.mail import send_mail
from django.forms import inlineformset_factory
from django.http import Http404
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.crypto import get_random_string
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from cw_dj import settings
from clients.forms import ClientForm, MessageForm, NewsletterForm, LoginUserForm, UserRegisterForm, UserProfileForm
from clients.mail_sender import mail_send
from clients.models import Client, Newsletter, Log, Message, User, Code


class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    extra_context = {
        'title': 'Клиенты'
    }

    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('clients:home')
    extra_context = {
        'title': 'Создание клиента'
    }


class ClientUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    permission_required = 'clients.change_client'
    success_url = reverse_lazy('clients:home')
    extra_context = {
        'title': 'Редактирование клиента'
    }

    def get_object(self, queryset=None):
        """
        Проверяет права доступа, если пользователь пытается редактировать не свой товар
        выкидывает ошибку Http404
        """
        obj = super().get_object(queryset)
        if obj.user != self.request.user:
            raise Http404("Вы не являетесь создателем этого клиента")
        return obj


class ClientBlockView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    permission_required = 'clients.change_client'
    model = Client
    success_url = reverse_lazy('clients:home')
    fields = ['is_blocked', ]

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.user != self.request.user:
            raise Http404("Вы не являетесь создателем этого клиента")
        return self.object


class Client_cardDetailView(LoginRequiredMixin, DetailView):
    model = Client

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.user != self.request.user:
            raise Http404("Вы не являетесь создателем этого клиента")
        return self.object

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        client_item = Client.objects.get(pk=self.kwargs.get('pk'))
        context_data['title'] = f'{client_item.full_name}'
        return context_data


class ClientDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Client
    permission_required = 'clients.delete_client'
    success_url = reverse_lazy('clients:home')
    extra_context = {
        'title': 'Удаление клиента'
    }

    def get_object(self, queryset=None):
        '''
        Проверяет права доступа, если пользователь пытается редактировать не свой товар
        выкидывает ошибку Http404
        '''
        self.object = super().get_object(queryset)
        if self.object.user != self.request.user:
            raise Http404("Вы не являетесь создателем этого клиента")
        return self.object


class NewsletterListView(LoginRequiredMixin, ListView):
    model = Newsletter
    extra_context = {
        'title': 'Рассылки'
    }


class Newsletter_cardDetailView(LoginRequiredMixin, DetailView):
    model = Newsletter

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.user != self.request.user:
            raise Http404("Вы не являетесь создателем этой рассылки")
        return self.object

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        if settings.CACHE_ENABLED:
            key = f'message_list_{self.object.pk}'
            message_list = cache.get(key)
            if message_list is None:
                message_list = self.object.messages.all()
                cache.set(key, message_list)
        else:
            message_list = self.object.messages.all()
        context_data['message_'] = message_list
        try:
            context_data['task'] = PeriodicTask.objects.get(name=kwargs['object'].id)
        except PeriodicTask.DoesNotExist:
            pass
        return context_data


class TaskToggleView(LoginRequiredMixin, UpdateView):
    model = PeriodicTask
    success_url = reverse_lazy('clients:newsletter_view')
    fields = []

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.enabled = not instance.enabled
        instance.save()
        return super().form_valid(form)


class NewsletterCreateView(LoginRequiredMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    success_url = reverse_lazy('clients:newsletter_view')
    extra_context = {
        'title': 'Создание рассылки'
    }

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        MessageFormset = inlineformset_factory(Newsletter, Message, form=MessageForm, extra=1)
        if self.request.method == 'POST':
            context_data['formset'] = MessageFormset(self.request.POST, instance=self.object)
        else:
            context_data['formset'] = MessageFormset(instance=self.object)
        return context_data

    def form_valid(self, form):
        formset = self.get_context_data()['formset']
        self.object = form.save(commit=False)
        self.object.status = Newsletter.STATUS_CREATED
        self.object.save()
        if formset.is_valid():
            formset.instance = self.object
            formset.save()
            super().form_valid(form)
            if datetime.datetime.now().time() > self.object.time:
                mail_send(newsletters=[self.object, ])
            cron = None
            if self.object.period == Newsletter.PERIOD_DAILY:
                cron = CrontabSchedule(
                    minute=str(self.object.time.minute),
                    hour=str(self.object.time.hour),
                    day_of_week='*',
                    day_of_month='*',
                    month_of_year='*',
                )
            elif self.object.period == Newsletter.PERIOD_WEEKLY:
                cron = CrontabSchedule(
                    minute=str(self.object.time.minute),
                    hour=str(self.object.time.hour),
                    day_of_month='*',
                    month_of_year='*',
                    day_of_week=datetime.datetime.now().weekday() + 1
                )
            elif self.object.period == Newsletter.PERIOD_MONTHLY:
                cron = CrontabSchedule(
                    minute=str(self.object.time.minute),
                    hour=str(self.object.time.hour),
                    day_of_week='*',
                    month_of_year='*',
                    day_of_month=str(datetime.datetime.now().day)
                )
            if cron:
                cron.save()
                PeriodicTask.objects.create(
                    name=f"{self.object.id}",
                    task="clients.tasks.mailing",
                    crontab=cron,
                    args=json.dumps([self.object.period]),
                )
        return super().form_valid(form)


class NewsletterDeleteView(LoginRequiredMixin, DeleteView):
    model = Newsletter
    success_url = reverse_lazy('clients:newsletter_view')
    extra_context = {
        'title': 'Удаление рассылки'
    }

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.user != self.request.user:
            raise Http404("Вы не являетесь создателем этой рассылки")
        return self.object


class LogListView(LoginRequiredMixin, ListView):
    model = Log
    extra_context = {
        'title': 'Лог'
    }


class UserLoginView(LoginView):
    form_class = LoginUserForm
    template_name = 'clients/login.html'
    success_url = reverse_lazy('clients:home')
    extra_context = {
        'title': 'Вход'
    }


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'clients/register.html'
    success_url = reverse_lazy('clients:confirm')

    def form_valid(self, form):
        code = get_random_string(6, '1234567890')
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        content_type = ContentType.objects.get_for_model(User)
        permission = Permission.objects.get(
            codename="manager_site_newsletter",
            content_type=content_type,
        )
        user.user_permissions.add(permission)
        Code.objects.create(
            code=code,
            user=user
        )
        self.request.session['user_id'] = user.id
        send_mail(
            subject='Верификация почты',
            message=f'Для верификации почты введите данный код {code}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        return redirect('clients:confirm')


class ConfirmView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'clients/confirm_account.html')

    def post(self, request, *args, **kwargs):
        user_id = request.session.get('user_id')
        # Получаем id пользователя
        user = User.objects.get(pk=user_id)
        code_user = request.POST.get('code_user')
        if not code_user:
            return redirect('clients:confirm')
        try:
            Code.objects.get(code=code_user, user=user)
        except Code.DoesNotExist:
            return render(request, 'clients/confirm_account.html', context={
                'error': 'Не верно введенный код'
            })
        user.is_active = True
        user.save()
        Code.objects.get(
            code=code_user,
            user=user
        ).delete()
        login(request, user)
        del request.session['user_id']
        return redirect('clients:login')


class ProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('clients:profile')

    def get_object(self, queryset=None):
        return self.request.user


def user_gen_password(request):
    user_email = request.POST.get("user_email")
    if not user_email:
        return redirect(reverse('clients:login'))
    try:
        user = User.objects.get(email=user_email)
    except User.DoesNotExist:
        return redirect(reverse('clients:login'))
    new_password = get_random_string(6, '1234567890')
    send_mail(
        subject='Сгенерированн новый пароль',
        message=f'Ваш пароль для авторизации {new_password}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[user_email]
    )
    user.set_password(new_password)
    user.save()
    return redirect(reverse('clients:login'))
