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
    检查域名是否是https
    """

    def __init__(self, domain: str):
        # 如果是 @.aa.com域名，则去掉 @.
        self.domain = ''.join(domain.strip().split("@.")[1]) if "@" in domain.strip() else domain.strip()

    def get_ssl_date(self):
        output = self.cmd_exec()
        start_date, expire_date = self.match_date(output)
        if start_date and expire_date:
            if self.does_not_match(output):
                return {"status": True, "start_date": start_date, "expire_date": expire_date,
                        "verify_https_msg": "域名与证书不匹配"}
            return {"status": True, "start_date": start_date, "expire_date": expire_date}
        else:
            return {"status": False}

    def does_not_match(self, s):
        m = re.search('does not match', s, re.S)
        if m:
            # 表示域名和证书不匹配
            return True
        else:
            return False

    def cmd_exec(self):
        cmd = F"curl -Ilvs https://{self.domain} --connect-timeout 5"
        result = subprocess.getstatusoutput(cmd)
        return result[1]

    def match_date(self, s):
        try:
            m = re.search('start date: (.*?)\n.*?expire date: (.*?)\n', s, re.S)
            start_date = m.group(1)
            expire_date = m.group(2)
            # datetime 字符串转时间数组
            start_date = datetime.strptime(start_date, "%b %d %H:%M:%S %Y GMT")
            expire_date = datetime.strptime(expire_date, "%b %d %H:%M:%S %Y GMT")
            remaining = (expire_date - datetime.now()).days  # 剩余天数

            print('*' * 30)
            print(F'https: [{self.domain} {start_date} {expire_date}] {remaining}天')
            print('*' * 30)

            return start_date, expire_date
        except AttributeError:
            # 没有匹配到证书的开始日期和结束日期
            pass
        except Exception:
            # 未知异常
            print(traceback.print_exc())
        print(F"http: [{self.domain}]")
        return None, None


def verify_https(domain):
    https = VerifyHttps(domain)
    return https.get_ssl_date()


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
        sub_domains = self.get_sub_domain()
        executor = ThreadPoolExecutor(30)
        https, http = [], []
        for i, data in enumerate(executor.map(verify_https, [item["name"] for item in sub_domains])):
            if data["status"]:
                if "verify_https_msg" in data:
                    sub_domains[i]["start_date"] = data["start_date"]
                    sub_domains[i]["expire_date"] = data["expire_date"]
                    sub_domains[i]["verify_https_msg"] = data["verify_https_msg"]
                else:
                    sub_domains[i]["start_date"] = data["start_date"]
                    sub_domains[i]["expire_date"] = data["expire_date"]
                https.append(sub_domains[i])
            else:
                http.append(sub_domains[i])

        return https, http


if __name__ == "__main__":
    # https = VerifyHttps("image4web.castleagegame.com")
    # output = https.cmd_exec()
    # print(https.get_ssl_date())
    #
    # exit(0)
    import json

    # print(time.asctime(time.localtime(time.time())))
    domain = ""
    # dnspod_account = {
    #     "id": "",
    #     "key": "",
    # }
    #
    # aliyun_account = {
    #     "key": "",
    #     "secret": "",
    # }
    #
    cloudflare_account = {
        "key": "",
        "email": "",
    }
    #
    dns = "cloudflare"
    domain_classify = DomainClassify(domain, dns, cloudflare_account)
    https, http = domain_classify.https_http_list()
    print(https)
    print(http)
    # print(time.asctime(time.localtime(time.time())))
