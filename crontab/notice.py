# 单独执行py文件时，首先载入django环境
# import os
# import django
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certificate_management.settings')
# django.setup()
#######
import json
from cert_app.models import DomainInfo, DnsApiAccounts
from scripts.py.verify_https import verify_https
import datetime
from scripts.py.query_sub_domain import query_subdomains
from scripts.py.custom_send_email import send_email

# 检查域名及子域名当证书过期时间小于5天时，发送通知邮件

number = 5


def json_serial(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()


def main():
    query_set = DomainInfo.objects.filter(status='valid')

    body = {}
    now_date = datetime.datetime.now()
    for item in query_set.values():
        label_1, label_2 = False, False

        pk = item["id"]
        domain = item["domain"]
        dns_company = item["dns_company"]
        to_email = item["to_email"]
        cc_email = item["cc_email"]

        # 域名对应的账号
        account_obj = DnsApiAccounts.objects.get(domain_info_id=pk)
        account = account_obj.account

        body["DNS"] = dns_company

        start_time, end_time = verify_https(domain)
        if end_time:
            remaining = (end_time - now_date).days

            if remaining <= number:
                body[domain] = {
                    "message": "证书即将到期, 请及时更换证书",
                    "剩余天数": remaining,
                    "有效期": end_time.strftime('%Y-%m-%d'),
                }

                label_1 = True

        https_list, _ = query_subdomains(domain, dns_company, account)

        for item in https_list:
            end_time = item["end_time"]
            remaining = (end_time - now_date).days

            if remaining <= number:
                body[item["name"]] = {
                    "message": "证书即将到期, 请及时更换证书",
                    "剩余天数": remaining,
                    "有效期": end_time.strftime('%Y-%m-%d'),
                }
                label_2 = True

        if label_1 or label_2:
            subject = F"{domain} 证书到期提醒"
            content = json.dumps(body, indent=4, ensure_ascii=False).replace(' ', '&nbsp;').replace("\n",
                                                                                                    "<br>").replace(
                '\"', '').replace("{", "").replace("}", "").replace(",", "")
            # 发送邮件
            send_email(subject, content, domain, to_email, cc_email)
        body.clear()


if __name__ == "__main__":
    main()
