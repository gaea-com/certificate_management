import logging
from scripts.py.verify_https import verify_https
from scripts.py.dns_api.dnspod import DNSPOD
from scripts.py.dns_api.aliyun import ALIYUN
from scripts.py.dns_api.cloudflare import CLOUDFLARE

logger = logging.getLogger('django')


# 查询创建证书时提交的域名的子域名
# 如提交的是 aa.bb.com 则只查询aa.bb.com下的子域名， 如 cc.aa.bb.com

def query_subdomains(domain=None, dns_company=None, account=None):
    """
    查询域名下的子域名，并校验哪些子域名启用了https
    返回httpsDomain list, httpDomain list
    :return: list, list 例: [{},{}] [{},{}]
    """

    subdomains_https = []
    subdomains_http = []

    c = eval(dns_company.upper())
    obj = c(domain, account)
    sub_domains = obj.part_sub_domains()

    for item in sub_domains:

        start_time, end_time = verify_https(item["name"])
        if end_time:
            item["start_time"] = start_time
            item["end_time"] = end_time
            subdomains_https.append(item)
        else:
            subdomains_http.append(item)

    return subdomains_https, subdomains_http


if __name__ == "__main__":
    import json

    domain = ""
    dnspod_account = {
        "id": "",
        "key": "",
    }

    aliyun_account = {
        "key": "",
        "secret": "",
    }

    cloudflare_account = {
        "key": "",
        "email": "",
    }

    dns_company = "cloudflare"
    https, http = query_subdomains(domain, dns_company, cloudflare_account)
    print(json.dumps(https))
    print(json.dumps(http))
