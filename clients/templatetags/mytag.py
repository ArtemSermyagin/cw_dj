import datetime
from django import template

register = template.Library()


@register.simple_tag
def current_time():
    dt_obj = datetime.datetime.now()
    dt_string = dt_obj.strftime("%d-%b-%Y")
    return dt_string


@register.filter()
def my_media(val):
    if val:
        return f'/media/{val}'
    else:
        return '#'