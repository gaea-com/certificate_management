import re
import logging
from cert_app.models import DomainInfo
from .verify_https import verify_https

logger = logging.getLogger('django')


def verify_domain(domain):
    """
    校验域名是否合法
    :param domain:
    :return: True/False
    """
    pattern = re.compile('(?i)^([a-z0-9\*]+(-[a-z0-9]+)*\.)+[a-z]{2,}$')
    match_domain = pattern.match(domain)

    if match_domain and "*" not in domain and len(domain) <= 63:
        return True

    return False


def verify_email(email):
    """
    校验邮箱格式是否正确
    :return: True/False
    """
    pattern = re.compile('^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$')
    match_email = pattern.match(email)

    if match_email:
        return True

    return False


def parameters_verify(**kwargs):
    """
    创建证书时，参数验证
    "domain", "dns_company", "to_email", "cc_email"
    """

    if "domain" in kwargs.keys():
        if not verify_domain(kwargs["domain"]):
            data = {
                "status": "failed",
                "message": F"不是有效的域名"
            }
            return data

        if DomainInfo.objects.filter(domain=kwargs["domain"]).exists():
            data = {
                "status": "failed",
                "message": F"域名已存在，请勿重复添加"
            }
            return data

    if "to_email" in kwargs.keys():
        if not verify_email(kwargs["to_email"]):
            data = {
                "status": "failed",
                "message": F"不是有效的接收邮箱地址"
            }
            return data

    if "cc_email" in kwargs.keys() and isinstance(kwargs["cc_email"], list):
        for email in kwargs["cc_email"]:
            if not verify_email(email):
                data = {
                    "status": "failed",
                    "message": F"不是有效的抄送邮箱地址"
                }
                return data

    data = {
        "status": "success",
        # "message": "",
        # "result": kwargs,
    }
    return data
