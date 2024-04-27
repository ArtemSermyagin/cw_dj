# Generated by Django 4.2.4 on 2024-04-27 16:05
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import migrations

from clients.models import User


def add_manager_newsletter_permission(apps, schema_editor):
    content_type = ContentType.objects.get_for_model(User)
    existing_permissions = Permission.objects.filter(content_type=content_type, codename='manager_site_newsletter')

    if not existing_permissions.exists():
        Permission.objects.create(
            codename='manager_site_newsletter',
            name='Менеджер',
            content_type=content_type,
        )


class Migration(migrations.Migration):
    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_manager_newsletter_permission)
    ]
