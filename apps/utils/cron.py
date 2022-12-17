from datetime import datetime, date, timedelta

from apps.models import Blog


def delete_blog():
    today = date.today()
    delta = timedelta(7)
    date_delta = today - delta
    Blog.cancel.filter(created_at__lt=date_delta).delete()
    print('adwsdawds')