import re
import time
import subprocess
import traceback
from datetime import datetime
from threading import Thread, activeCount
from concurrent.futures import ThreadPoolExecutor, as_completed
from res.dns_api.dnspod import DNSPOD
from res.dns_api.cloudflare import CLOUDFLARE
from res.dns_api.aliyun import ALIYUN
from res.utils.DNS import QueryDNSResolver


class VerifyHttps(object):
    """
    验证传进来的域名是否有证书，如果没有，刚解析此域名，对解析的地址逐个验证是否有证书
    """

    def __init__(self, domain: str):
        self.domain = domain.strip()

    def get_ssl_date(self):
        start_date, expire_date = self.exec_cmd(self.domain)
        if expire_date:
            return start_date, expire_date
        else:
            dns_resolver = QueryDNSResolver(self.domain)
            address_list = dns_resolver.A_query()
            for address in address_list:
                start_date, expire_date = self.exec_cmd(address)
                if expire_date:
                    return start_date, expire_date
            return None, None

    def exec_cmd(self, domain):
        domain = domain.strip()
        domain = ''.join(domain.split("@.")[1]) if "@" in domain else domain
        cmd = F"curl -lvs https://{domain} --connect-timeout 5"
        result = subprocess.getstatusoutput(cmd)
        try:
            m = re.search('start date: (.*?)\n.*?expire date: (.*?)\n', result[1], re.S)
            start_date = m.group(1)
            expire_date = m.group(2)

            # datetime 字符串转时间数组
            start_date = datetime.strptime(start_date, "%b %d %H:%M:%S %Y GMT")
            expire_date = datetime.strptime(expire_date, "%b %d %H:%M:%S %Y GMT")

            # 剩余天数
            remaining = (expire_date - datetime.now()).days

            print('*' * 30)
            print(F'域名: [{self.domain} --> {domain}]')
            print(F'开始时间: {start_date}')
            print(F'到期时间: {expire_date}')
            print(F'剩余时间: {remaining}天')
            print('*' * 30)
            return start_date, expire_date
        except AttributeError as e:
            pass
        except Exception:
            print(traceback.print_exc())

        print(F"http: [{self.domain} --> {domain}]")
        return None, None


class VerifyHttpsThread(Thread):
    def __init__(self, domain):
        super().__init__()
        self.domain = domain

    def run(self):
        verify_https = VerifyHttps(self.domain)
        self.result = verify_https.get_ssl_date()

    def get_result(self):
        return self.result


class DomainClassify(object):
    """
    域名分类:
        http
        https
    """

    def __init__(self, domain: str, dns: str, account: dict):
        self.domain = domain.strip()
        self.dns = dns
        self.account = account

    def get_sub_domain(self):
        """
        获取域名下的子域名
        """
        dns_list = [DNSPOD, CLOUDFLARE, ALIYUN]  # 此变量没有用到
        cls = eval(self.dns.upper())
        obj = cls(self.domain, self.account)
        sub_domains = obj.part_sub_domains()
        return sub_domains

    def https_http_list(self):
        """
        域名分类:
            https: list
            http: list
        return: https list, http list
        例: ([{},{}], [{},{}])
        """
        # # 线程池，默认30个
        # sub_domains = self.get_sub_domain()
        # executor = ThreadPoolExecutor(30)
        # https, http = [], []
        # verify_https = VerifyHttps(self.domain)
        # for i, data in enumerate(executor.map(verify_https, [item["name"] for item in sub_domains])):
        #     if data[0]:
        #         sub_domains[i]["start_date"] = data[0]
        #         sub_domains[i]["expire_date"] = data[1]
        #         https.append(sub_domains[i])
        #     else:
        #         http.append(sub_domains[i])
        #
        # return https, http

        sub_domains = self.get_sub_domain()
        max_thread_nums = 30
        thread_list = []
        for item in sub_domains:
            t = VerifyHttpsThread(item["name"])
            t.start()
            thread_list.append(t)

            while True:
                if activeCount() < max_thread_nums:
                    break
                time.sleep(0.5)

        https, http = [], []
        for i, t in enumerate(thread_list):
            t.join()
            while t.isAlive():
                time.sleep(1)

            start_date, expire_date = t.get_result()
            if start_date:
                sub_domains[i]["start_date"] = start_date
                sub_domains[i]["expire_date"] = expire_date
                https.append(sub_domains[i])
            else:
                http.append(sub_domains[i])
        return https, http


if __name__ == "__main__":
    # print(verify_https(""))
    import json

    print(time.asctime(time.localtime(time.time())))
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

    dns = "dnspod"
    domain_classify = DomainClassify(domain, dns, dnspod_account)
    https, http = domain_classify.https_http_list()
    print(https)
    print(http)
    print(time.asctime(time.localtime(time.time())))
