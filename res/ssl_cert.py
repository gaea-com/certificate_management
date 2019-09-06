import os
import logging
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from ssl_cert.models import Domain, SSLCertContent
from res.acme import Acme
from apps.ssl_cert.config import CERT_DIR
from res.domain import DomainClassify
from res.email_table.ssl_create_email_table import email_table
from res.custom_send_email import send_email
from ssl_cert.to_email import to_email as to

log = logging.getLogger('django')
User = get_user_model()


def save_ssl_cert(domain_obj):
    """
    将证书保存在数据库中
    """
    cert_file = os.path.join(CERT_DIR, domain_obj.domain, "fullchain.cer")
    key_file = os.path.join(CERT_DIR, domain_obj.domain, F"{domain_obj.domain}.key")
    with open(cert_file, 'r') as cf, open(key_file, 'r') as kf:
        SSLCertContent.objects.update_or_create(
            domain=domain_obj,
            defaults={
                "cert_content": cf.read(),
                "key_content": kf.read(),
            }
        )
    log.info(F"{domain_obj.domain} ssl cert save to database")


class SSLCert(object):
    def __init__(self, domain: str, ext_domain_open: bool, dns: str, account: dict):
        self.domain = domain
        self.ext_domain_open = ext_domain_open
        self.dns = dns
        self.account = account

    def create(self):
        """
        创建证书
        """
        status = self.exec_task("create")
        self.db_operation(status, "create")
        https_list, http_list = self.get_subdomain_list(status)
        content = email_table(status, self.domain, self.dns, https_list, http_list)  # 格式化成html table作为邮件内容发送
        subject = F"{self.domain} 证书创建成功" if status else F"{self.domain} 证书创建失败"
        to_email = to(self.domain)
        send_email(subject, content, self.domain, to_email)

    def update(self):
        """
        更新证书
        """
        status = self.exec_task("create")
        self.db_operation(status, "update")
        https_list, http_list = self.get_subdomain_list(status)
        content = email_table(status, self.domain, self.dns, https_list, http_list)  # 格式化成html table作为邮件内容发送
        subject = F"{self.domain} 证书更新成功" if status else F"{self.domain} 证书更新失败"
        to_email = to(self.domain)
        send_email(subject, content, self.domain, to_email)

    def get_subdomain_list(self, status: bool):
        """
        获取域名下的子域名,并分类
            https list
            http list
        """

        # 证书创建或更新失败时，不查询其子域名
        if status:
            domain_classify = DomainClassify(self.domain, self.dns, self.account)
            https_list, http_list = domain_classify.https_http_list()
        else:
            https_list, http_list = None, None

        return https_list, http_list

    def db_operation(self, status: bool, action: str):
        """
        创建/更新证书成功时，将域名修改为有效状态，失败时，将域名修改为无效状态
        """
        domain_obj = Domain.objects.get(domain=self.domain)
        if status:
            domain_obj.status = "valid"
            domain_obj.start_date = datetime.now()
            domain_obj.expire_date = datetime.now() + timedelta(days=90)
            domain_obj.save()
            save_ssl_cert(domain_obj)
        else:
            domain_obj.status = "failed"
            if action == "create":
                domain_obj.expire_date = datetime.now()
            domain_obj.save()

    def exec_task(self, action):
        """
        执行创建/更新证书
        """
        acme = Acme(self.domain, self.dns, self.account, self.ext_domain_open)
        status = eval("acme.%s()" % action)  # 创建/更新证书
        log.info(F"{action} ssl cert: [{self.domain}], status: [{status}]")
        log.info((acme.get_stdout()).decode("utf-8"))
        return status


if __name__ == '__main__':
    # 单独执行py文件时，首先载入django环境
    import os
    import django

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'new_ssl_cert.settings')
    django.setup()
    #######
    domain = ""
    dns = ""
    account = {
        "key": "",
        "email": "",
    }
    # extensive_domain_open = False
    # create_ssl_cert(domain, extensive_domain_open, dns, account)
