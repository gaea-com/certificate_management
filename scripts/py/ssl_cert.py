# 单独执行py文件时，首先载入django环境
# import os
# import django
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certificate_management.settings')
# django.setup()
#######
import os
import logging
import traceback
from datetime import datetime, timedelta

from django import db

from .acme import Acme
from cert_app.conf import CERT_DIR
from cert_app.models import DomainInfo, CertContent
from .custom_send_email import send_email
from .format_table import table
from .query_sub_domain import query_subdomains

logger = logging.getLogger('django')

"创建ssl证书"


def save_cert_content(obj):
    """
    保存fullchain.cer、 key文件内容到数据库中
    :param obj: DomainInfo
    :return:
    """

    if not isinstance(obj, DomainInfo):
        logger.error("only receive an object of type DomainInfo")
        return False

    cert_file = os.path.join(CERT_DIR, obj.domain, "fullchain.cer")
    key_file = os.path.join(CERT_DIR, obj.domain, f"{obj.domain}.key")

    with open(cert_file, 'r') as cf, open(key_file, 'r') as kf:
        CertContent.objects.update_or_create(
            domain_info_id=obj.id,
            defaults={
                "cert_content": cf.read(),
                "key_content": kf.read()
            }
        )
        logger.info(f"{cert_file} content save to db")
        logger.info(f"{key_file} content save to db")


def ssl_cert(domain=None, dns_company=None, account=None, to_email=None, cc_email=None,
             request_host=None):
    """
    创建证书
    :return:
    """
    try:
        # 需要先把数据库连接关闭，重新建立连接
        # for alias, info in db.connections.databases.items():
        #     db.close_old_connections()
        #     logger.info("db close alias: {}".format(alias))
        #     logger.info("db close info: {}".format(info))

        # 创建证书
        acme = Acme()
        create_ret = acme.create_cert(dns_company, account, domain)

        if create_ret:
            logger.info(f"ssl cert create success: {domain}")

            DomainInfo.objects.filter(domain=domain).update(status="valid")

            # 将证书和key保存到数据库中
            save_cert_content(DomainInfo.objects.filter(domain=domain).first())

            # 获取子域名
            https_list, http_list = query_subdomains(domain, dns_company, account)
            # 将子域名格式化成html table样子
            t_ = table(domain, https_list, http_list)

            subject = "{} 证书创建成功".format(domain)

            space = "&nbsp;" * 4
            content = F"""
                        {space}域  名: {domain} <br>
                        {space}状  态: 证书创建成功 <br>
                        {space}有效期: {(datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")} <br>
                        {space}查看证书: http://{request_host}/cert <br><br>
                    """ + (t_ if t_ else "<br><br><br><br><br><br>")
        else:
            DomainInfo.objects.filter(domain=domain).update(status="failed")

            # 获取失败报错信息
            stdout_info = acme.get_cmd_exec_ret()
            logger.info("证书创建失败: {}\n{}".format(domain, stdout_info.decode("utf-8")))

            subject = "{} 证书创建失败".format(domain)
            content = """
                        域  名: {}<br>
                        状  态: 证书创建失败<br><br>
                        报错信息:<br>
                        {}<br>
                    """.format(domain, stdout_info.decode("utf-8").replace("\n", "<br>"))

    except Exception:
        DomainInfo.objects.filter(domain=domain).update(status="failed")

        logger.error(f"create ssl cert unknown exception: {domain}")
        logger.error(traceback.format_exc())

        subject = f"{domain} 创建证书时发生未知异常"
        content = "ERROR,创建证书时发生未知异常，请检查<br><br>"

    # 发送邮件
    send_email(subject, content, domain, to_email, cc_email)


if __name__ == '__main__':
    pass
