from clients.models import Client, Newsletter, Message, Log, User
from django.contrib import admin


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    permissions = (
        ("manager_site_newsletter", "Менеджер"),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name', 'comment', 'avatar', 'is_blocked')
    search_fields = ('full_name',)


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('id', 'time', 'period', 'status',)
    search_fields = ('period',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'theme', 'letter',)
    search_fields = ('theme',)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_attempt', 'state', 'response_server',)
    search_fields = ('state',)

