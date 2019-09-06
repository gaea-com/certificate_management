# 单独执行py文件时，首先载入django环境
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'new_ssl_cert.settings')
django.setup()
######
import logging
from datetime import datetime, timedelta
from ssl_cert.models import Domain
from django.contrib.auth import get_user_model
from res.custom_send_email import send_email
from res.domain import VerifyHttps
from res.domain import DomainClassify
from res.email_table.ssl_expired_alarms_email_table import email_table
from ssl_cert.to_email import to_email as to
from res.utils.SLD import SLD
from res.ssl_cert import SSLCert

User = get_user_model()
log = logging.getLogger("django")


def domain_filter(days):
    """
    查询小于指定天数的域名
    """
    filter_time = datetime.now() + timedelta(days=days)
    # queryset = Domain.objects.filter(expire_date__lte=filter_time, status="valid")
    queryset = Domain.objects.filter(expire_date__lte=filter_time)
    return queryset


def auto_update_ssl_cert():
    """
    证书距离过期日期 小于等于 7天时，自动更新证书
    """
    days = 7
    queryset = domain_filter(days)
    for obj in queryset:
        ssl_cert = SSLCert(obj.domain, obj.extensive_domain, obj.dns, eval(obj.dns_account))
        ssl_cert.update()


class SSLCertExpiredAlarms(object):
    """
    检查所有域名及子域名当证书过期时间小于5天时，发送通知邮件
    """

    def __init__(self):
        self.days = 50  # 证书距离过期剩余天数

    def alarms(self):
        # acme创建的免费证书有效期最多90天，这里过滤100之内的域名，即所有域名
        queryset = domain_filter(100)
        for obj in queryset:
            ssl_cert_status, expire_date = self.main_domain(obj.domain)
            https_sub_domain = self.https_sub_domain_filter(obj.domain, obj.dns, eval(obj.dns_account))

            if https_sub_domain and not expire_date:
                # 如果有即将过期的子域名，但主域名没有走https，刚从数据库中查询主域名的过期时间
                ssl_cert_status, expire_date = self.main_domain_from_db(obj.domain)

            if ssl_cert_status or https_sub_domain:
                # 主域名即将过期，或者 子域名即将过期 发送通知通知
                sld = SLD(obj.domain)
                # 如果是个二级域名，在发送邮件时，前面加上@
                new_domain = "@." + obj.domain if sld.reg_match() else obj.domain
                email_content = email_table(ssl_cert_status, new_domain, obj.dns, expire_date, https_sub_domain)
                subject = F"{new_domain} SSL证书过期提醒"
                to_email = to(obj.domain)
                send_email(subject, email_content, obj.domain, to_email)

    def main_domain(self, domain):
        """
        检查主域名是否即将过期
        """
        verify_https = VerifyHttps(domain)
        start_date, expire_date = verify_https.get_ssl_date()
        if expire_date:
            remaining = (expire_date - datetime.now()).days
            if remaining <= self.days:
                return True, expire_date  # True 表示即将过期
        return False, expire_date  # False 表示离过期还有一段时间

    def main_domain_from_db(self, domain):
        """
        在数据库查询域名的过期时间
        """
        # 如果域名不是https，则从数据库中查询域名的过期时间
        queryset = Domain.objects.filter(domain=domain)
        expire_date = queryset.values()[0]["expire_date"]
        remaining = (expire_date - datetime.now()).days
        if remaining <= self.days:
            return True, expire_date  # True 表示即将过期
        return False, expire_date  # False 表示离过期还有一段时间

    def https_sub_domain_filter(self, domain, dns, account):
        """
        查询即将到期的子域名
        """
        domain_classify = DomainClassify(domain, dns, account)
        https_list, _ = domain_classify.https_http_list()  # 获取域名下的所有https子域名
        new_https_list = []
        for item in https_list:
            remaining = (item["expire_date"] - datetime.now()).days
            if remaining <= self.days:
                new_https_list.append(item)

        print(F"new https list: {new_https_list}")
        return new_https_list


def expired_alarms():
    """
    SSL证书过期提醒
    """
    alarms = SSLCertExpiredAlarms()
    alarms.alarms()


if __name__ == '__main__':
    pass