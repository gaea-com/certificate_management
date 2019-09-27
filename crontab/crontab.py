# 单独执行py文件时，首先载入django环境
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'new_ssl_cert.settings')
django.setup()
######
import logging
from datetime import datetime, timedelta
from ssl_cert.models import Domain, CustomDomain
from django.contrib.auth import get_user_model
from res.custom_send_email import send_email
from res.domain import VerifyHttps
from res.domain import DomainClassify
from res.email_table.ssl_expired_alarms_email_table import email_table
from res.email_table.custom_domain_ssl_expired_alarms import custom_domain_alarm_email
from ssl_cert.to_email import to_email, custom_domain_to_email
from res.utils.SLD import SLD
from res.ssl_cert import SSLCert

User = get_user_model()
log = logging.getLogger("django")


def domain_filter(days):
    """
    查询小于指定天数的域名
    """
    filter_time = datetime.now() + timedelta(days=days)
    queryset = Domain.objects.filter(expire_date__lte=filter_time, status="valid")
    return queryset


def auto_update_ssl_cert():
    """
    执行计划 执行函数
    证书距离过期日期 小于等于 7天时，自动更新证书
    """
    days = 7
    queryset = domain_filter(days)
    log.info(F"auto update domain: [{queryset.values('domain')}]")
    for obj in queryset:
        ssl_cert = SSLCert(obj.domain, obj.extensive_domain, obj.dns, eval(obj.dns_account))
        ssl_cert.update()


class SSLCertExpiredAlarms(object):
    """
    检查所有域名及子域名当证书过期时间小于5天时，发送通知邮件
    """

    def __init__(self):
        self.days = 5  # 证书距离过期剩余天数

    def alarms(self):
        # acme创建的免费证书有效期最多90天，这里过滤有效期100天之内的域名，即所有域名
        queryset = domain_filter(1000)
        for obj in queryset:
            main_domain_result = self.main_domain(obj.domain, obj.source_ip)
            https_sub_domain = self.https_sub_domain_filter(obj.domain, obj.dns, eval(obj.dns_account))

            # 域名与证书不匹配、主域名即将过期、子域名即将过期 发送邮件通知
            if "verify_https_msg" in main_domain_result \
                    or main_domain_result["expire"] or https_sub_domain:
                log.info(F"expire alarm main domain: {obj.domain}")
                log.info(F"expire alarm sub domain: {https_sub_domain}")
                sld = SLD(obj.domain)
                new_domain = "@." + obj.domain if sld.is_sld() else obj.domain  # 如果是个二级域名，在发送邮件时，前面加上@
                email_content = email_table(new_domain, obj.dns, main_domain_result, https_sub_domain)
                subject = F"{new_domain} SSL证书过期提醒"
                email = to_email(obj.domain)
                send_email(subject, email_content, obj.domain, email)

    def main_domain(self, domain: str, source_ip: str = None):
        """
        检查主域名是否即将过期
            先检查域名本身是否是https
            如果不是https, 则看是否有添加源站IP
            如果有, 则通过源站IP检查证书是否到期
            如果源站上也没有证书, 则从数据库中查询主域名的过期时间
        """
        verify_https = VerifyHttps(domain)
        result = verify_https.get_ssl_date()
        if not result["status"]:
            if source_ip:
                result = verify_https.get_source_ip_ssl_date(source_ip)
                if not result["status"]:
                    result = self.main_domain_from_db(domain)
            else:
                result = self.main_domain_from_db(domain)

        remaining = (result["expire_date"] - datetime.now()).days
        # True 表示即将过期 # False 表示离过期还有一段时间
        if "verify_https_msg" in result:
            if remaining <= self.days:
                return {"expire": True, "expire_date": result["expire_date"],
                        "verify_https_msg": result["verify_https_msg"]}
            else:
                return {"expire": False, "expire_date": result["expire_date"],
                        "verify_https_msg": result["verify_https_msg"]}
        if remaining <= self.days:
            return {"expire": True, "expire_date": result["expire_date"]}
        else:
            return {"expire": False, "expire_date": result["expire_date"]}

    def main_domain_from_db(self, domain):
        """
        在数据库查询域名的过期时间
        """
        # 从数据库中查询域名的过期时间
        queryset = Domain.objects.filter(domain=domain)
        expire_date = queryset.values()[0]["expire_date"]
        return {"expire_date": expire_date}

    def https_sub_domain_filter(self, domain, dns, account):
        """
        查询即将到期的子域名
        """
        domain_classify = DomainClassify(domain, dns, account)
        https_list, _ = domain_classify.https_http_list()  # 获取域名下的所有https子域名
        new_https_list = []
        for item in https_list:
            remaining = (item["expire_date"] - datetime.now()).days
            if "verify_https_msg" in item:
                new_https_list.append(item)
                continue
            if remaining <= self.days:
                item["expire"] = True
                new_https_list.append(item)

        return new_https_list


def expired_alarms():
    """
    执行计划 执行函数
    SSL证书过期提醒
    """
    alarms = SSLCertExpiredAlarms()
    alarms.alarms()


def custom_domain_filter(days):
    """
    查询小于指定天数的自定义域名
    """
    filter_time = datetime.now() + timedelta(days=days)
    queryset = CustomDomain.objects.filter(expire_date__lte=filter_time)
    return queryset


def custom_domain_expired_alarms():
    """
    执行计划 执行函数
    自定义域名SSL证书过期提醒
    """
    days = 5
    queryset = custom_domain_filter(days)
    log.info(F"custom domain expire alarms: {queryset.values()}")
    for obj in queryset:
        custom_domain = obj.domain
        expire_date = obj.expire_date
        content = custom_domain_alarm_email(custom_domain, expire_date)
        subject = F"{custom_domain} SSL证书过期提醒"
        email = custom_domain_to_email(custom_domain)
        send_email(subject, content, custom_domain, email)


if __name__ == '__main__':
    # expired_alarms()
    custom_domain_expired_alarms()
