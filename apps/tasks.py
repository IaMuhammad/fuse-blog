from celery import shared_task

from apps.models import CustomUser


@shared_task(bind=True)
def senf_mail_func(self):
    user = CustomUser.objects.all()
    return 'Done'