import logging
import requests
import traceback
import json
from requests.exceptions import ConnectTimeout
from apps.ssl_cert.config import dns_api_mode

# CloudFlare查询子域名接口
logger = logging.getLogger('django')


class CLOUDFLARE(object):
    def __init__(self, domain, account):
        self.domain = domain
        self.key = account[dns_api_mode["cloudflare"][0]]
        self.email = account[dns_api_mode["cloudflare"][1]]
        self.TIMEOUT = 30
        self.second_level_domain = '.'.join(domain.split('.')[-2:])
        self.base_url = "https://api.cloudflare.com/client/v4/zones"

    def request_headers(self):
        """
        请求头
        """
        headers = {
            'Content-Type': 'application/json',
            "X-Auth-Key": self.key,
            "X-Auth-Email": self.email,
        }
        return headers

    def get_zone_id(self):
        """
        查询zone id
        :return: id|None
        """
        try:
            payload = {
                "page": 1,
                "per_page": 20,
                "match": "all",
            }
            r = requests.get(self.base_url, headers=self.request_headers(), params=payload, timeout=self.TIMEOUT)
            status = r.json()["success"]
            total_pages = r.json()["result_info"]["total_pages"]
            result = r.json()["result"]

            if not status:
                logger.error("request failed")
                logger.error(r.text)
                return None

            zone_id = None
            page = 1
            while page <= total_pages:
                for item in result:
                    if item["name"] == self.second_level_domain:
                        zone_id = item["id"]
                        return zone_id

                page += 1
                payload = {
                    "page": page,
                    "per_page": 20,
                    "match": "all",
                }

                r = requests.get(self.base_url, headers=self.request_headers(), params=payload, timeout=self.TIMEOUT)
                result = r.json()["result"]

            if not zone_id:
                logger.error(F"cat not get zone id: {r.text}")

        except ConnectTimeout as e:
            logger.error(F"get zone id timeout: {e}")
        except Exception:
            logger.error(F"get zone id unknown exception")
            logger.error(traceback.format_exc())

    def get_record_id(self, zone_id: str, sub_domain: str) -> str:
        """
        查询记录id
        """
        try:
            sub_domain = sub_domain.lower()
            dns_record_url = self.base_url + "/" + zone_id + "/" + "dns_records"
            payload = {
                "page": 1,
                "per_page": 20,
                "match": "all",
            }
            r = requests.get(dns_record_url, headers=self.request_headers(), params=payload, timeout=self.TIMEOUT)
            status = r.json()["success"]
            total_pages = r.json()["result_info"]["total_pages"]
            result = r.json()["result"]
            if not status:
                logger.error(F"query record failed: {r.text}")
                return ""
            identifier = None
            for page in range(1, total_pages + 1):
                for item in result:
                    if item["name"] == sub_domain + "." + self.domain:
                        identifier = item["id"]
                        return identifier
                page += 1
                if page == total_pages + 1:
                    break

                payload = {
                    "page": page,
                    "per_page": 20,
                    "match": "all",
                }
                r = requests.get(dns_record_url, headers=self.request_headers(), params=payload, timeout=self.TIMEOUT)
                result = r.json()["result"]

            if not identifier:
                logger.error(F"cat not get record id: {r.text}")
        except ConnectTimeout as e:
            logger.error(F"get record id timeout: {e}")
        except Exception:
            logger.error(F"get record id unknown exception")
            logger.error(traceback.format_exc())

    def part_sub_domains(self):
        """
        查询域名下的所有子域名
        :return: list
        """
        try:
            zone_id = self.get_zone_id()

            payload = {
                "page": 1,
                "per_page": 20,
                "match": "all",
            }
            records_url = self.base_url + "/" + zone_id + "/" + "dns_records"
            r = requests.get(records_url, headers=self.request_headers(), params=payload, timeout=self.TIMEOUT)
            status = r.json()["success"]
            total_pages = r.json()["result_info"]["total_pages"]
            result = r.json()["result"]
            if not status:
                logger.error(F"query record failed: {r.text}")
                return None

            data = []
            for page in range(1, total_pages + 1):
                for item in result:
                    # 过滤掉"MX", "TXT", "SRV"类型的记录
                    if item["name"] != self.domain and item["type"] not in ("MX", "TXT", "SRV", "NS") and \
                            item["name"].endswith(self.domain):
                        data.append(
                            {
                                # "name": ".".join(item["name"].split(".")[0:-2]),
                                "name": item["name"],
                                "type": item["type"],
                                # "line": None,
                                "value": item["content"],
                                # "mx": item["priority"] if "priority" in item else "0",
                                # "ttl": item["ttl"],
                                # "status": "正常",
                            }
                        )

                page += 1
                if page == total_pages + 1:
                    break
                payload = {
                    "page": page,
                    "per_page": 20,
                    "match": "all",
                }
                r = requests.get(records_url, headers=self.request_headers(), params=payload, timeout=self.TIMEOUT)
                result = r.json()["result"]

            return data
        except ConnectTimeout as e:
            logger.error(F"get sub domains failed: {e}")
        except Exception:
            logger.error(F"get sub domains unknown exception")
            logger.error(traceback.format_exc())

    def sub_domains(self, part=None):
        """
        查询域名下的所有子域名
        :return: list
        """
        try:
            zone_id = self.get_zone_id()

            payload = {
                "page": 1,
                "per_page": 20,
                "match": "all",
            }
            records_url = self.base_url + "/" + zone_id + "/" + "dns_records"
            r = requests.get(records_url, headers=self.request_headers(), params=payload, timeout=self.TIMEOUT)
            status = r.json()["success"]
            total_pages = r.json()["result_info"]["total_pages"]
            result = r.json()["result"]
            if not status:
                logger.error(F"query record failed: {r.text}")
                return None

            data = []
            for page in range(1, total_pages + 1):
                for item in result:
                    if part:
                        # 过滤掉"MX", "TXT", "SRV"类型的记录
                        if item["name"] != self.domain and item["type"] not in ("MX", "TXT", "SRV", "NS") and \
                                item["name"].endswith(self.domain):
                            data.append(
                                {
                                    # "name": ".".join(item["name"].split(".")[0:-2]),
                                    "name": item["name"],
                                    "type": item["type"],
                                    "line": None,
                                    "value": item["content"],
                                    "mx": item["priority"] if "priority" in item else "0",
                                    "ttl": item["ttl"],
                                    "status": "正常",
                                }
                            )
                    else:
                        data.append(
                            {
                                # "name": ".".join(item["name"].split(".")[0:-2]),
                                "name": item["name"],
                                "type": item["type"],
                                "line": None,
                                "value": item["content"],
                                "mx": item["priority"] if "priority" in item else "0",
                                "ttl": item["ttl"],
                                "status": "正常",
                            }
                        )

                page += 1
                if page == total_pages + 1:
                    break
                payload = {
                    "page": page,
                    "per_page": 20,
                    "match": "all",
                }
                r = requests.get(records_url, headers=self.request_headers(), params=payload, timeout=self.TIMEOUT)
                result = r.json()["result"]

            return data
        except ConnectTimeout as e:
            logger.error(F"get sub domains failed: {e}")
        except Exception:
            logger.error(F"get sub domains unknown exception")
            logger.error(traceback.format_exc())

    def add_record(self, sub_domain=None, record_type=None, line=None, record_value=None, ttl=None, priority=None):
        """
        添加域名记录
        :return: True|False
        """
        try:
            zone_id = self.get_zone_id()
            add_record_url = self.base_url + "/" + zone_id + "/" + "dns_records"
            if record_type == "显示URL" or record_type == "隐性URL":
                record_type = "URI"
            payload = {
                "type": record_type,
                "name": sub_domain + "." + self.domain,
                "content": record_value,
                # "ttl": 120 if int(ttl) < 120 else int(ttl),
                "ttl": 1,  # 值为1，自动生效
            }
            if record_type == "MX":
                payload.update({"priority": priority})
            r = requests.post(add_record_url, headers=self.request_headers(), data=json.dumps(payload),
                              timeout=self.TIMEOUT)
            status = r.json()["success"]
            if status:
                logger.info(F"add record success: {sub_domain}")
                return True
            logger.error(F"add record failed: {r.text}")
        except ConnectTimeout:
            logger.error(F"add record timeout: {sub_domain}")
        except UnboundLocalError:
            logger.error(F"add record failed, not found domain, please check api account: [{self.key} : {self.email}]")
        except Exception:
            logger.error(F"add record unknown exception")
            logger.error(traceback.format_exc())
        return False

    def delete_record(self, sub_domain=None):
        """
        删除记录
        :return: True|False
        """
        try:
            zone_id = self.get_zone_id()
            record_id = self.get_record_id(zone_id, sub_domain)
            del_record_url = self.base_url + "/" + zone_id + "/" + "dns_records" + "/" + record_id
            r = requests.delete(del_record_url, headers=self.request_headers(), timeout=self.TIMEOUT)
            status = r.json()["success"]
            if status:
                logger.info(F"del record success: {sub_domain}")
                return True
            logger.error(F"del record failed: {r.text}")
        except ConnectTimeout as e:
            logger.error(F"del record timeout: {e}")
        except TypeError:
            logger.error(F"zone_id or record_id is null ?")
        except Exception:
            logger.error("del record unknown exception")
            logger.error(traceback.format_exc())

    def modify_record(self, old_sub_domain=None, new_sub_domain=None, record_type=None,
                      line=None, record_value=None, ttl=None, priority=None):
        """
        修改记录
        :return: True|False
        """
        try:
            zone_id = self.get_zone_id()
            record_id = self.get_record_id(zone_id, old_sub_domain)
            modify_record_url = self.base_url + "/" + zone_id + "/" + "dns_records" + "/" + record_id
            if record_type == "显示URL" or record_type == "隐性URL":
                record_type = "URI"
            payload = {
                "type": record_type,
                "name": new_sub_domain + "." + self.domain,
                "content": record_value,
                "ttl": 1,  # 值为1，自动生效
            }
            if record_type == "MX":
                payload.update({"priority": priority})
            r = requests.put(modify_record_url, headers=self.request_headers(), data=json.dumps(payload), timeout=10)
            status = r.json()["success"]
            if status:
                return True
            logger.error(F"modify record failed: {r.text}")
        except ConnectTimeout as e:
            logger.error(F"modify record timeout: {e}")
        except Exception:
            logger.error("modify record unknown exception")
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    domain = ""
    account = {
        "key": "",
        "email": ""
    }

    sub_domain = "verify_domain_JOdWq1SI"
    # record_type = "CNAME"
    # record_value = "www.baidu.com"

    # old_sub_domain = "test-blog"
    # new_sub_domain = "aaa-blog"
    # record_type = "A"
    # record_value = "1.1.1.1"
    #
    cloudflare = CLOUDFLARE(domain, account)
    # ret = cloudflare.add_record(sub_domain=sub_domain, record_type="TXT", line=None, record_value="123", ttl=None, priority=None)
    # print((ret))
    # ret = cloudflare.delete_record(sub_domain=sub_domain)
    # print(ret)
