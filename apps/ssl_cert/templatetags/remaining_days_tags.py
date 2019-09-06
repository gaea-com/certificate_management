import datetime
from django import template

register = template.Library()


@register.simple_tag
def remaining_days(expire_date):
    """
    过期时间减去当前时间得到剩余天数
    """
    if expire_date:
        now_time = datetime.datetime.now()
        new_expire_date = datetime.datetime.strptime(expire_date, '%Y-%m-%d %H:%M:%S')
        return F"{(new_expire_date - now_time).days} 天"
    return ""
