import requests
from requests.exceptions import ConnectTimeout
from apps.ssl_cert.config import dns_api_mode
from res.utils.SLD import SLD
from json.decoder import JSONDecodeError

# DnsPod 查询子域名接口

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
        self.domain = domain.strip()
        self.id_ = account[dns_api_mode["dnspod"][0]]
        self.token = account[dns_api_mode["dnspod"][1]]
        self.TIMEOUT = 30
        sld = SLD(self.domain)
        self.sub, self.sld = sld.domain_cut()

    def request(self, url: str, **kwargs) -> dict:
        """
        执行请求
        """
        kwargs.update({
            "login_token": "{},{}".format(self.id_, self.token),  # id_ 和 key以逗号分割
            "format": "json",
            "domain": self.sld,
        })
        try:
            r = requests.post(url, data=kwargs, timeout=self.TIMEOUT)
            if r.json()["status"]["code"] == "1":
                return r.json()
            else:
                print(F"[{self.sld}] request error: {r.text}")
                return {"status": {"code": 0}}
        except ConnectTimeout as e:
            print(F"[{self.sld}] request timeout: {e}")
            return {"status": {"code": 0}}
        except JSONDecodeError as e:
            print(F"[{self.sld}] request login failed: {e}")
            return {"status": {"code": 0}}

    def record_list(self, offset: int = 0, length: int = 3000) -> dict:
        """
        查询所有记录
        """
        url = "https://dnsapi.cn/Record.List"
        payload = {
            "offset": offset,
            "length": length,
        }
        response = self.request(url, **payload)
        return response

    def record_id(self, sub_domain: str) -> str:
        """
        查询子域名的记录ID
        """
        offset = 0
        length = 3000
        while True:
            response = self.record_list(offset, length)
            if response["status"]["code"] == str(1):
                records = response["records"]
                sub_domain = sub_domain + "." + self.sub if self.sub else sub_domain
                record_id = ','.join([record["id"] for record in records if record["name"] == sub_domain])
                if record_id:
                    return record_id
                else:
                    offset = offset + length
            else:
                print(F"cat not get [{self.domain} -> {sub_domain}] record id")
                return ""

    def sub_domains(self) -> list:
        """
        查询子域名
            统一所有记录的存储格式，用于前端子域名页面调用、检查子域名是否为https接口调用
        """
        offset = 0
        length = 3000
        sub_domains_list = []
        types_ = ("MX", "TXT", "SRV", "NS")  # 过滤掉"MX", "TXT", "SRV", "NS"类型的记录
        while True:
            response = self.record_list(offset, length)
            if response["status"]["code"] == str(1):
                records = response["records"]
                for item in records:
                    if item["name"] != self.sub and item["type"] not in types_ and item['name'].endswith(self.sub):
                        sub_domains_list.append(
                            {
                                "name": item["name"] + "." + self.sld,
                                "type": item["type"],
                                "line": item["line"],
                                "value": item["value"],
                                "mx": item["mx"],
                                "ttl": item["ttl"],
                                "status": "正常" if item["enabled"] == "1" else "暂停",
                            }
                        )
                if (offset + length) >= int(response["info"]["record_total"]):
                    break
                else:
                    offset = offset + length
            else:
                break
        return sub_domains_list

    def add_record(self, sub_domain: str, record_type: str, record_line: str, record_value: str, ttl: int = 600,
                   mx: int = 10) -> bool:
        """
        添加记录
        """
        url = "https://dnsapi.cn/Record.Create"
        if record_type in ("显示URL", "隐性URL"):
            record_type = "URL"

        payload = {
            "sub_domain": sub_domain + ("." + self.sub if self.sub else ""),
            "record_type": record_type.upper(),
            "record_line": record_line,
            "value": record_value,
            "ttl": 600 if int(ttl) < 600 or int(ttl) > 604800 else int(ttl),
            "mx": mx,
        }
        response = self.request(url, **payload)
        if response["status"]["code"] == str(1):
            return True
        else:
            return False

    def delete_record(self, sub_domain: str) -> bool:
        """
        删除记录
        """
        url = "https://dnsapi.cn/Record.Remove"
        record_id = self.record_id(sub_domain)
        if not record_id:
            return False
        payload = {
            "record_id": record_id,
        }
        response = self.request(url, **payload)
        if response["status"]["code"] == str(1):
            return True
        else:
            return False

    def set_record_status(self, sub_domain: str, status: str) -> bool:
        """
        设置记录的状态
        status {enable|disable}
        """
        url = "https://dnsapi.cn/Record.Status"
        record_id = self.record_id(sub_domain)
        if not record_id:
            return False
        payload = {
            "record_id": record_id,
            "status": status.lower(),
        }
        response = self.request(url, **payload)
        if response["status"]["code"] == str(1):
            return True
        else:
            return False

    def modify_record(self, old_sub_domain: str, new_sub_domain: str, record_type: str, record_line: str,
                      record_value: str, ttl: int = 600, mx: int = 10) -> bool:
        """
        修改记录
        """
        url = "https://dnsapi.cn/Record.Modify"
        record_id = self.record_id(old_sub_domain)
        if not record_id:
            return False

        if record_type in ("显示URL", "隐性URL"):
            record_type = "URL"

        payload = {
            "record_id": record_id,
            "sub_domain": new_sub_domain + ("." + self.sub if self.sub else ""),
            "record_type": record_type.upper(),
            "record_line": record_line,
            "value": record_value,
            "ttl": 600 if int(ttl) < 600 or int(ttl) > 604800 else int(ttl),
            "mx": mx,
        }
        response = self.request(url, **payload)
        if response["status"]["code"] == str(1):
            return True
        else:
            return False


if __name__ == "__main__":
    domain = ""
    account = {
        "id": "",
        "token": "",
    }
