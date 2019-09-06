import logging
import requests
import traceback
from requests.exceptions import ConnectTimeout
from apps.ssl_cert.config import dns_api_mode

# DnsPod 查询子域名接口
logger = logging.getLogger('django')

__record_doc__ = """
    "types": [
        "A",
        "CNAME",
        "MX",
        "TXT",
        "NS",
        "AAAA",
        "SRV",
        "URL"
    ]
    "line_ids": {
        "默认": 0,
        "国内": "7=0",
        "国外": "3=0",
        "电信": "10=0",
        "联通": "10=1",
        "教育网": "10=2",
        "移动": "10=3",
        "百度": "90=0",
        "谷歌": "90=1",
        "搜搜": "90=4",
        "有道": "90=2",
        "必应": "90=3",
        "搜狗": "90=5",
        "奇虎": "90=6",
        "搜索引擎": "80=0"
    },
    "lines": [
        "默认",
        "国内",
        "国外",
        "电信",
        "联通",
        "教育网",
        "移动",
        "百度",
        "谷歌",
        "搜搜",
        "有道",
        "必应",
        "搜狗",
        "奇虎",
        "搜索引擎"
    ]
    """


class DNSPOD(object):
    def __init__(self, domain: str, account: dict):
        # self.domain = domain
        self.id_ = account[dns_api_mode["dnspod"][0]]
        self.token = account[dns_api_mode["dnspod"][1]]
        self.TIMEOUT = 10
        if domain.endswith(".com.cn") or \
                domain.endswith(".net.cn") or \
                domain.endswith(".ac.cn"):
            self.prefix_domain = '.'.join(domain.split(".")[0:-3])
            self.second_level_domain = '.'.join(domain.split('.')[-3:])
        else:
            self.prefix_domain = '.'.join(domain.split(".")[0:-2])
            self.second_level_domain = '.'.join(domain.split('.')[-2:])

    def get_record_list(self) -> list:
        """
        查询域名所有的记录
        """
        try:
            URL = "https://dnsapi.cn/Record.List"
            payload = {
                "login_token": "{},{}".format(self.id_, self.token),  # id_ 和 key以逗号分割
                "format": "json",
                "domain": self.second_level_domain,
                "offset": 0,
                "length": 10000,
            }
            r = requests.post(URL, data=payload, timeout=self.TIMEOUT)
            if r.json()["status"]["code"] == "1":
                return r
            else:
                logger.error(F"Failed to query record list: {r.text}")
                return None
        except ConnectTimeout:
            logger.error(F"query record failed: {self.second_level_domain}")

    def get_record_id(self, sub_domain: str) -> int:
        """
        查询记录对应的id
        """
        sub_domain = sub_domain.lower()
        request = self.get_record_list()
        if request:
            records = request.json()['records']
            if self.prefix_domain:
                sub_domain = ''.join([sub_domain, ".", self.prefix_domain])
            record_id = ','.join([record["id"] for record in records if record["name"] == sub_domain])
            if record_id:
                return record_id
            else:
                logger.error(F"can not get record id: {sub_domain}")
                return None

    def part_sub_domains(self) -> dict:
        """
        统一所有记录的存储格式, 用于查询子域名
        """

        request = self.get_record_list()
        if request:
            records = request.json()['records']
            data = []
            for item in records:
                # 过滤掉"MX", "TXT", "SRV"类型的记录
                if item['name'] != self.prefix_domain and item["type"] not in ("MX", "TXT", "SRV", "NS") \
                        and item['name'].endswith(self.prefix_domain):
                    data.append(
                        {
                            "name": item["name"] + "." + self.second_level_domain,
                            "type": item["type"],
                            # "line": item["line"],
                            "value": item["value"],
                            # "mx": item["mx"],
                            # "ttl": item["ttl"],
                            # "status": "正常" if item["enabled"] == "1" else "暂停",
                        }
                    )
            return data

    def sub_domains(self, part=None) -> dict:
        """
        统一所有记录的存储格式, 用于DNS解析页面
        """
        request = self.get_record_list()
        if request:
            records = request.json()['records']
            data = []
            for item in records:
                # 过滤掉"MX", "TXT", "SRV"类型的记录
                if part:
                    if item['name'] != self.prefix_domain and item["type"] not in ("MX", "TXT", "SRV", "NS") \
                            and item['name'].endswith(self.prefix_domain):
                        data.append(
                            {
                                "name": item["name"] + "." + self.second_level_domain,
                                "type": item["type"],
                                "line": item["line"],
                                "value": item["value"],
                                "mx": item["mx"],
                                "ttl": item["ttl"],
                                "status": "正常" if item["enabled"] == "1" else "暂停",
                            }
                        )
                else:
                    data.append(
                        {
                            "name": item["name"] + "." + self.second_level_domain,
                            "type": item["type"],
                            "line": item["line"],
                            "value": item["value"],
                            "mx": item["mx"],
                            "ttl": item["ttl"],
                            "status": "正常" if item["enabled"] == "1" else "暂停",
                        }
                    )
            return data

    def add_record(self, sub_domain=None, record_type=None, record_line=None, value=None, ttl=600, mx=None) -> bool:
        """
        添加记录
        """
        try:
            URL = "https://dnsapi.cn/Record.Create"
            if record_type == "显示URL" or record_type == "隐性URL":
                record_type = "URL"
            payload = {
                "login_token": "{},{}".format(self.id_, self.token),  # id_ 和 token以逗号分割
                "format": "json",
                "domain": self.second_level_domain,
                "sub_domain": sub_domain + ("." + self.prefix_domain if self.prefix_domain else ""),
                "record_type": record_type.upper(),
                "record_line": record_line,
                "value": value,
                "ttl": 600 if int(ttl) < 600 else int(ttl),
            }
            if record_type == "MX":
                payload.update({"mx": mx})

            r = requests.post(URL, data=payload, timeout=self.TIMEOUT)
            code = r.json()["status"]["code"]
            if code == "1":
                logger.info(F"add record success: {sub_domain}")
                return True
            logger.error(F"add record failed: {r.text}")
        except ConnectTimeout as e:
            logger.error(F"add record failed: {e}")
        except Exception:
            logger.error("add record unknown exception")
            logger.error(traceback.format_exc())

    def delete_record(self, sub_domain=None) -> bool:
        """
        删除记录
        """
        try:
            URL = "https://dnsapi.cn/Record.Remove"
            record_id = self.get_record_id(sub_domain)
            if not record_id:
                return False
            payload = {
                "login_token": "{},{}".format(self.id_, self.token),  # id_ 和 token以逗号分割
                "format": "json",
                "domain": self.second_level_domain,
                "record_id": record_id,
            }
            r = requests.post(URL, data=payload, timeout=self.TIMEOUT)
            code = r.json()["status"]["code"]
            if code == "1":
                logger.info(F"del record success: {sub_domain}")
                return True
            logger.error(F"del record failed: {r.text}")
        except ConnectTimeout as e:
            logger.error(F"del record timeout: {e}")
        except Exception:
            logger.error("del record unknown exception")
            logger.error(traceback.format_exc())

    def set_record_status(self, sub_domain=None, status=None) -> bool:
        """
        设置记录的状态
        status {enable|disable}
        """
        try:
            URL = "https://dnsapi.cn/Record.Status"
            record_id = self.get_record_id(sub_domain)
            if not record_id:
                return False
            payload = {
                "login_token": "{},{}".format(self.id_, self.token),  # id_ 和 token以逗号分割
                "format": "json",
                "domain": self.second_level_domain,
                "record_id": record_id,
                "status": status.lower(),
            }
            r = requests.post(URL, data=payload, timeout=self.TIMEOUT)
            code = r.json()["status"]["code"]
            if code == "1":
                logger.info(F"set record status success: [{sub_domain} : {status}]")
                return True
            logger.error(F"set record status failed: {r.text}")
        except ConnectTimeout as e:
            logger.error(F"set record status timeout: {e}")
        except Exception:
            logger.error("set record unknown exception")
            logger.error(traceback.format_exc())

    def modify_record(self, old_sub_domain=None, new_sub_domain=None, record_type=None, record_line=None, value=None,
                      ttl=None, mx=None) -> bool:
        """
        修改记录
        """
        try:
            URL = "https://dnsapi.cn/Record.Modify"
            record_id = self.get_record_id(old_sub_domain)
            if not record_id:
                return False
            if record_type == "显示URL" or record_type == "隐性URL":
                record_type = "URL"
            payload = {
                "login_token": "{},{}".format(self.id_, self.token),  # id_ 和 token以逗号分割
                "format": "json",
                "domain": self.second_level_domain,
                "record_id": record_id,
                "sub_domain": new_sub_domain + "." + self.prefix_domain,
                "record_type": record_type.upper(),
                "record_line": record_line,
                "value": value,
                "ttl": 600 if int(ttl) < 600 else int(ttl),
            }
            if record_type == "MX":
                payload.update({"mx": mx})
            r = requests.post(URL, data=payload, timeout=self.TIMEOUT)
            code = r.json()["status"]["code"]
            if code == "1":
                return True
            logger.error(F"modify record failed: {r.text}")
        except ConnectTimeout as e:
            logger.error(F"modify record timeout: {e}")
        except Exception:
            logger.error("modify record unknown exception")
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    domain = "xjqxz.gaeamobile.net"
    account = {
        "id": "35700",
        "token": "edacfc51d99cde2098aabae9cbc231f1",
    }
    record_type = "A"
    record_line = "默认"
    value = "1.1.1.1"
    ttl = 600
    status = "enable"
    sub_domain = "verify_domain_dx5xlpmt"
    old_sub_domain = "fff"
    new_sub_domain = "a2-test"
    dnspod = DNSPOD(domain, account)
    # dnspod.get_record_list()
    print(dnspod.get_record_id(sub_domain))
