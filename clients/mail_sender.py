from datetime import datetime

from django.db.models import Prefetch
from django.core.mail import send_mail

from cw_dj import settings
from clients.models import Newsletter, Log


def mail_send(period=None, newsletters=None):
    if not period and not newsletters:
        return None
    if not newsletters:
        newsletters = Newsletter.objects.filter(period=period)
    for newsletter in newsletters:
        messages = newsletter.messages.all()
        newsletter.status = Newsletter.STATUS_STARTED
        newsletter.save()
        logs = []
        recipients = newsletter.client.filter(is_blocked=False).values_list('email', flat=True)
        for message in messages:
            try:
                logs.append(Log(
                    date_attempt=datetime.now(),
                    state=Newsletter.STATUS_STARTED,
                    response_server="200",
                    message=message
                ))
                send_mail(
                    subject=message.theme,
                    message=message.letter,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=recipients,
                )
                logs.append(Log(
                    date_attempt=datetime.now(),
                    state=Newsletter.STATUS_DONE,
                    response_server="200",
                    message=message
                ))
            except Exception as e:
                logs.append(Log(
                    date_attempt=datetime.now(),
                    state='1',
                    response_server=str(e),
                    message=message
                ))

        Log.objects.bulk_create(logs)
        newsletter.status = Newsletter.STATUS_DONE
        newsletter.save()
