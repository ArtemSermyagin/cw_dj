from datetime import datetime

from django.core.mail import send_mail

from clients.models import Newsletter, Log
from cw_dj import settings

from django.core.management import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        newsletters = Newsletter.objects.all()
        for newsletter in newsletters:
            messages = newsletter.messages.all()
            for client in newsletter.client.all():
                for message in messages:
                    try:
                        Log.objects.create(
                            date_attempt=datetime.now(),
                            state=Newsletter.STATUS_STARTED,
                            response_server="200",
                            message=message
                        )
                        send_mail(
                            subject=message.theme,
                            message=message.letter,
                            from_email=settings.EMAIL_HOST_USER,
                            recipient_list=[client.email],
                        )
                        Log.objects.create(
                            date_attempt=datetime.now(),
                            state=Newsletter.STATUS_DONE,
                            response_server="200",
                            message=message
                        )
                    except Exception as e:
                        Log.objects.create(
                            date_attempt=datetime.now(),
                            state='1',
                            response_server=str(e),
                            message=message
                        )
