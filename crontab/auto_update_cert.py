# 单独执行py文件时，首先载入django环境
# import os
# import django
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certificate_management.settings')
# django.setup()
#######
import logging
import datetime
import os

from cert_app.models import DomainInfo, DnsApiAccounts, CertContent
from scripts.py.acme import Acme
from scripts.py.custom_send_email import send_email
from cert_app.conf import CERT_DIR
from scripts.py.format_table import table
from scripts.py.query_sub_domain import query_subdomains

logger = logging.getLogger('django')


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


def main():
    """
    证书距离过期时间 <= 7天时，自动更新证书, 并将证书通过邮箱发送给接收者
    :return: None
    """
    DAYS = 7

    now_date = datetime.datetime.now()
    all_objects = DomainInfo.objects.filter(status="valid")

    for item in all_objects.values():
        pk = item["id"]
        domain = item["domain"]
        end_time = item["end_time"].replace(tzinfo=None)
        # end_time = item["end_time"]
        dns_company = item["dns_company"]

        to_email = item["to_email"]
        cc_email = item["cc_email"]

        # 域名对应的账号
        account_obj = DnsApiAccounts.objects.get(domain_info_id=pk)
        account = account_obj.account

        # 证书剩余天数
        remaining_date = (end_time - now_date).days
        # new_start_date = now_date.strftime("%Y-%m-%d")
        new_end_date = now_date + datetime.timedelta(days=90)

        logger.info(F"remaining days: [{domain} : {remaining_date}]")

        if remaining_date <= DAYS:
            # 创建证书
            acme = Acme()
            create_ret = acme.create_cert(dns_company, account, domain)

            if create_ret:
                logger.info(f"auto update ssl cert: {domain}")
                # 修改数据中域名对应的时间
                update_obj = DomainInfo.objects.get(id=pk)
                update_obj.start_time = now_date
                update_obj.end_time = new_end_date
                update_obj.save()

                # 将证书和key保存到数据库中
                save_cert_content(DomainInfo.objects.filter(id=pk).first())

                https_list, http_list = query_subdomains(domain, dns_company, account)

                # 将子域名格式化成html table样子
                t_ = table(domain, https_list, http_list)

                subject = F"{domain} 证书已更新"

                space = "&nbsp;" * 4
                content = F"""
                            {space}域  名: {domain} <br>
                            {space}状  态: 证书已更新 <br>
                            {space}旧证书剩余天数: {remaining_date} <br>
                            {space}新证书有效期: {new_end_date.strftime("%Y-%m-%d")} <br><br>
                            """ + (t_ if t_ else "<br><br><br><br><br><br>")

            else:
                logger.error(F"{domain} 自动更新失败")
                # 自动更新失败，修改域名的status 为 failed
                update_obj = DomainInfo.objects.get(id=pk)
                update_obj.status = "failed"
                update_obj.save()

                # 获取acme命令创建证书时的报错信息
                stdout_info = acme.get_cmd_exec_ret()
                subject = F"{domain} 证书自动更新失败"
                content = """
                            域  名: {}<br>
                            状  态: 证书自动更新失败<br><br>
                            报错信息:<br>
                            {}<br>
                        """.format(domain, stdout_info.decode("utf-8").replace("\n", "<br>"))

            # 发送邮件
            send_email(subject, content, domain, to_email, cc_email)


if __name__ == "__main__":
    main()
