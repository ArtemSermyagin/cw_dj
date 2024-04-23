from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .models import User

content_type = ContentType.objects.get_for_model(User)
existing_permissions = Permission.objects.filter(content_type=content_type, codename='manager_site_newsletter')
manager_newsletter_permission = Permission.objects.create(
    codename='manager_site_newsletter',
    name='Менеджер',
    content_type=content_type,
)
