import requests
import traceback
import json
from requests.exceptions import ConnectTimeout
from apps.ssl_cert.config import dns_api_mode
from res.utils.SLD import SLD


# CloudFlare查询子域名接口


class CLOUDFLARE(object):
    def __init__(self, domain: str, account: dict):
        self.domain = domain.strip()
        self.key = account[dns_api_mode["cloudflare"][0]]
        self.email = account[dns_api_mode["cloudflare"][1]]
        self.TIMEOUT = 60
        self.base_url = "https://api.cloudflare.com/client/v4/"
        sld = SLD(self.domain)
        _, self.sld = sld.domain_cut()

    def request_headers(self):
        """
        请求头
        """
        headers = {
            'Content-Type': 'application/json',
            "X-Auth-Key": self.key,
            "X-Auth-Email": self.email,
            "order": "type",
            "direction": "asc",
        }
        return headers

    def request(self, method: str, url: str, page: int = 1, **kwargs) -> dict:
        """
        执行请求
        """
        params = {
            "page": page,
            "per_page": 50,
            "match": "all",
        }
        try:
            if method == "GET":
                r = requests.get(url, headers=self.request_headers(), params=params, timeout=self.TIMEOUT)
            elif method == "POST":
                r = requests.post(url, headers=self.request_headers(), data=json.dumps(kwargs), timeout=self.TIMEOUT)
            elif method == "DELETE":
                r = requests.delete(url, headers=self.request_headers(), timeout=self.TIMEOUT)
            elif method == "PUT":
                r = requests.put(url, headers=self.request_headers(), data=json.dumps(kwargs), timeout=self.TIMEOUT)
            else:
                return {"result": list()}
            if not r.json()["success"]:
                print(F"[{self.sld}] {method} request error: {r.text}")
            return r.json()
        except ConnectTimeout as e:
            print(F"[{self.sld}] {method} request timeout: {e}")
            return {"result": list()}

    def zone_id(self) -> str:
        """
        查询zone id
        """
        url = self.base_url + "zones"
        page = 1
        while True:
            response = self.request("GET", url, page)
            result = response["result"]
            if result:
                zone_id = [item["id"] for item in result if item["name"] == self.sld]
                if zone_id:
                    return ''.join(zone_id)
                else:
                    page += 1
            else:
                print(F"cat not get [{self.sld}] zone id")
                return ""

    def record_id(self, sub_domain: str) -> tuple:
        """
        查询记录ID
        返回 zone id, record id
        """
        zone_id = self.zone_id()
        url = self.base_url + "zones/" + zone_id + "/dns_records"
        page = 1
        while True:
            response = self.request("GET", url, page)
            result = response["result"]
            if result:
                record_id = [item["id"] for item in result if item["name"] == sub_domain + "." + self.domain]
                if record_id:
                    return zone_id, ''.join(record_id)
                else:
                    page += 1
            else:
                print(F"cat not get [{self.sld} -> {sub_domain}] record id")
                return "", ""

    def sub_domains(self):
        """
        查询子域名
        """
        zone_id = self.zone_id()
        url = self.base_url + "zones/" + zone_id + "/dns_records"
        page = 1
        sub_domains_list = []
        types_ = ("MX", "TXT", "SRV", "NS")  # 过滤掉"MX", "TXT", "SRV", "NS"类型的记录
        while True:
            response = self.request("GET", url, page)
            result = response["result"]
            if result:
                for item in result:
                    if item["name"] != self.domain and item["type"] not in types_ and item["name"].endswith(
                            self.domain):
                        sub_domains_list.append(
                            {
                                "name": item["name"],
                                "type": item["type"],
                                "line": None,
                                "value": item["content"],
                                "mx": item["priority"] if "priority" in item else "0",
                                "ttl": item["ttl"],
                                "status": "正常",
                            }
                        )
                if page >= response["result_info"]["total_pages"]:
                    break
                else:
                    page += 1
            else:
                break
        return sub_domains_list

    def add_record(self, sub_domain: str, record_type: str, line: str, record_value: str, ttl: int = 1,
                   priority: int = 10) -> bool:
        """
        添加记录
        """
        line = None  # cloudflare没有这项参数，加上这俩参数是为了与dnspod、阿里云接口保持一致
        zone_id = self.zone_id()
        url = self.base_url + "zones/" + zone_id + "/dns_records"
        if record_type in ("显示URL", "隐性URL"):
            record_type = "URI"

        payload = {
            "type": record_type,
            "name": sub_domain + "." + self.domain,
            "content": record_value,
            "ttl": 1,  # 值为1，自动生效
            "priority": priority,  # 优化级
            "proxied": False,  #
        }
        response = self.request("POST", url, **payload)
        if response["success"]:
            return True
        else:
            return False

    def delete_record(self, sub_domain: str) -> bool:
        """
        删除记录
        """
        zone_id, record_id = self.record_id(sub_domain)
        url = self.base_url + "zones/" + zone_id + "/dns_records/" + record_id
        response = self.request("DELETE", url)
        if response["success"]:
            return True
        else:
            return False

    def modify_record(self, old_sub_domain: str, new_sub_domain: str, record_type: str, line: str, record_value: str,
                      ttl: int = 1, priority: int = 10):
        """
        修改记录
        """
        line = None  # cloudflare没有这项参数，加上这俩参数是为了与dnspod、阿里云接口保持一致
        zone_id, record_id = self.record_id(old_sub_domain)
        url = self.base_url + "zones/" + zone_id + "/dns_records/" + record_id
        if record_type in ("显示URL", "隐性URL"):
            record_type = "URI"

        payload = {
            "type": record_type,
            "name": new_sub_domain + "." + self.domain,
            "content": record_value,
            "ttl": 1,  # 值为1，自动生效
            "priority": priority,  # 优化级
            "proxied": False,  #
        }
        response = self.request("PUT", url, **payload)
        print(response)
        if response["success"]:
            return True
        else:
            return False


if __name__ == "__main__":
    domain = ""
    account = {
        "key": "",
        "email": ""
    }
