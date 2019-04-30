import datetime
from django import template

register = template.Library()


@register.simple_tag
def remaining_days(endtime):
    if endtime:
        now_time = datetime.datetime.now()
        new_end_time = datetime.datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S')
        return F"{(new_end_time - now_time).days} 天"
    return ""
