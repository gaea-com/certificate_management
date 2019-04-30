# 单独执行py文件时，首先载入django环境
# import os
# import django
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certificate_management.settings')
# django.setup()
#######

import logging
from cert_app.models import DomainInfo, SubDomains, DnsApiAccounts
from scripts.py.query_sub_domain import query_subdomains

logger = logging.getLogger('django')


def main():
    """
    将域名下的子域名分别按https, http分类保存在数据库中
    :return: None
    """
    try:
        domain_info = DomainInfo.objects.filter(status="valid")

        # 清空表中的记录，以防有新的子域名变更，表中的记录不能及时删除
        # SubDomains.objects.all().delete()

        for row in domain_info.values():
            pk = row["id"]
            domain = row["domain"]
            dns_company = row["dns_company"]

            account_obj = DnsApiAccounts.objects.filter(domain_info_id=pk).first()
            account = account_obj.account

            https_ret, http_ret = query_subdomains(domain, dns_company, account)

            for item in https_ret:
                if not SubDomains.objects.filter(sub_domain=item["name"]).exists():
                    SubDomains(
                        protocol="https",
                        sub_domain=item["name"],
                        record_type=item["type"],
                        record_value=item["value"],
                        start_time=item["start_time"],
                        end_time=item["end_time"],
                        domain_info_id=pk
                    ).save()
                    logger.info(F"HTTPS subdomain saved: {item['name']} ")

            for item in http_ret:
                if not SubDomains.objects.filter(sub_domain=item["name"]).exists():
                    SubDomains(
                        protocol="http",
                        sub_domain=item["name"],
                        record_type=item["type"],
                        record_value=item["value"],
                        domain_info_id=pk
                    ).save()
                    logger.info(F"HTTP subdomain saved: {item['name']} ")

    except Exception:
        logger.error("save sub domain unknown exception")


if __name__ == "__main__":
    main()
