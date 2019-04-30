import logging
import requests
import traceback
import json
from requests.exceptions import ConnectTimeout
from cert_app.conf import dns_api_mode

# CloudFlare查询子域名接口
logger = logging.getLogger('django')


# def sub_domains(domain=None, key=None, email=None):
#     """
#     返回所有子域名列表
#     :param domain: str
#     :param key: str
#     :param email: str
#     :return: list
#     """
#     try:
#         top_domain = '.'.join(domain.split('.')[-2:])
#         url = "https://api.cloudflare.com/client/v4/zones"
#         headers = {
#             'Content-Type': 'application/json',
#             "X-Auth-Key": key,
#             "X-Auth-Email": email,
#         }
#         payload = {
#             "page": 1,
#             "per_page": 20,
#             "match": "all",
#         }
#
#         r = requests.get(url, headers=headers, params=payload, timeout=10)
#         status = r.json()["success"]
#         total_pages = r.json()["result_info"]["total_pages"]
#         result = r.json()["result"]
#
#         if not status:
#             logger.error("cloudflare请求失败")
#             logger.error(r.text)
#             return []
#
#         zone_id = ""
#         page = 1
#         while page <= total_pages:
#             for item in result:
#                 if item["name"] == top_domain:
#                     zone_id = item["id"]
#                     break
#
#             page += 1
#             payload = {
#                 "page": page,
#                 "per_page": 20,
#                 "match": "all",
#             }
#             r = requests.get(url, headers=headers, params=payload, timeout=10)
#             result = r.json()["result"]
#
#         if not zone_id:
#             logger.error("没有查询%s对应的 zone id" % domain)
#             return []
#
#         url = url + "/" + zone_id + "/" + "dns_records"
#         r = requests.get(url, headers=headers, timeout=10)
#         status = r.json()["success"]
#
#         if status:
#             result = r.json()["result"]
#             subdomains = []
#             for item in result:
#                 if item["name"] != domain and item["type"] != "TXT" and item["name"].endswith(domain):
#                     subdomains.append(
#                         {
#                             "sub_domain": item["name"],
#                             "record_type": item["type"],
#                             "record_value": item["content"]
#                         }
#                     )
#
#             return subdomains
#
#         logger.error(r.json()["errors"])
#
#     except UnboundLocalError as e:
#         logger.error("请检查CloudFlare {} 账号下是否有 {} 域名".format(email, domain))
#         logger.error(traceback.format_exc())
#
#     except Exception as e:
#         logger.error("cloudflare_subdomains_record 未知异常")
#         logger.error(traceback.format_exc())
#
#     return []
#
#
# def get_all_sub_domain(domain=None, key=None, email=None):
#     """
#     查询顶级域名下所有的子域名
#     :param domain: str
#     :param key: str
#     :param email: str
#     :return: list
#     """
#     try:
#         top_domain = '.'.join(domain.split('.')[-2:])
#         url = "https://api.cloudflare.com/client/v4/zones"
#         headers = {
#             'Content-Type': 'application/json',
#             "X-Auth-Key": key,
#             "X-Auth-Email": email,
#         }
#         payload = {
#             "page": 1,
#             "per_page": 20,
#             "match": "all",
#         }
#
#         r = requests.get(url, headers=headers, params=payload, timeout=10)
#         status = r.json()["success"]
#         total_pages = r.json()["result_info"]["total_pages"]
#         result = r.json()["result"]
#
#         if not status:
#             logger.error("cloudflare请求失败")
#             logger.error(r.text)
#             return []
#
#         zone_id = ""
#         page = 1
#         while page <= total_pages:
#             for item in result:
#                 if item["name"] == top_domain:
#                     zone_id = item["id"]
#                     break
#
#             page += 1
#             payload = {
#                 "page": page,
#                 "per_page": 20,
#                 "match": "all",
#             }
#
#             r = requests.get(url, headers=headers, params=payload, timeout=10)
#             result = r.json()["result"]
#
#         if not zone_id:
#             logger.error("没有查询%s 对应的 zone id" % domain)
#             return []
#
#         payload = {
#             "page": 1,
#             "per_page": 1000,
#             "match": "all",
#         }
#
#         url = url + "/" + zone_id + "/" + "dns_records"
#         r = requests.get(url, headers=headers, params=payload, timeout=10)
#         status = r.json()["success"]
#         total_pages = r.json()["result_info"]["total_pages"]
#         result = r.json()["result"]
#         if not status:
#             logger.error("域名记录查询失败")
#             logger.error(r.text)
#             return []
#
#         data = []
#         for page in range(1, total_pages + 1):
#             for item in result:
#                 if item["type"] == "MX":
#                     continue
#                 data.append(
#                     {
#                         # "name": ".".join(item["name"].split(".")[0:-2]),
#                         "name": item["name"],
#                         "type": item["type"],
#                         "line": None,
#                         "value": item["content"],
#                         "ttl": item["ttl"],
#                         "status": "正常",
#                     }
#                 )
#
#             page += 1
#             if page == total_pages + 1:
#                 break
#             payload = {
#                 "page": page,
#                 "per_page": 1000,
#                 "match": "all",
#             }
#             r = requests.get(url, headers=headers, params=payload, timeout=10)
#             status = r.json()["success"]
#             if not status:
#                 logger.error("域名记录查询失败")
#                 logger.error(r.text)
#                 return []
#             result = r.json()["result"]
#
#         return data
#
#     except UnboundLocalError as e:
#         logger.error("请检查CloudFlare {} 账号下是否有 {} 域名".format(email, domain))
#         logger.error(traceback.format_exc())
#
#     except Exception as e:
#         logger.error("cloudflare_subdomains_record 未知异常")
#         logger.error(traceback.format_exc())
#
#     return []
#
#
# def add_record(domain=None, key=None, email=None, sub_domain=None, record_type=None, line=None, record_value=None,
#                ttl=None, priority=None):
#     """
#     查询顶级域名下所有的子域名
#     :param domain: str
#     :param key: str
#     :param email: str
#     :return: list
#     """
#     try:
#         top_domain = '.'.join(domain.split('.')[-2:])
#         base_url = "https://api.cloudflare.com/client/v4/zones"
#
#         headers = {
#             'Content-Type': 'application/json',
#             "X-Auth-Key": key,
#             "X-Auth-Email": email,
#         }
#         payload = {
#             "page": 1,
#             "per_page": 20,
#             "match": "all",
#         }
#
#         r = requests.get(base_url, headers=headers, params=payload, timeout=10)
#         status = r.json()["success"]
#         total_pages = r.json()["result_info"]["total_pages"]
#         result = r.json()["result"]
#
#         if not status:
#             logger.error("cloudflare请求失败")
#             logger.error(r.text)
#             return []
#
#         zone_id = ""
#         page = 1
#         while page <= total_pages:
#             for item in result:
#                 if item["name"] == top_domain:
#                     zone_id = item["id"]
#                     break
#
#             page += 1
#             payload = {
#                 "page": page,
#                 "per_page": 20,
#                 "match": "all",
#             }
#
#             r = requests.get(base_url, headers=headers, params=payload, timeout=10)
#             result = r.json()["result"]
#
#         if not zone_id:
#             logger.error("没有查询%s 对应的 zone id" % domain)
#             return []
#
#         url = base_url + "/" + zone_id + "/" + "dns_records"
#         if record_type == "显示URL" or record_type == "隐性URL":
#             record_type = "URI"
#
#         payload = {
#             "type": record_type,
#             "name": sub_domain + "." + top_domain,
#             "content": record_value,
#             # "ttl": 120 if int(ttl) < 120 else int(ttl),
#             "ttl": 1,  # 值为1，自动生效
#         }
#
#         if record_type == "MX":
#             payload.update({"priority": priority})
#
#         r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
#         status = r.json()["success"]
#         if status:
#             return True
#
#         logger.error(r.text)
#
#     except UnboundLocalError as e:
#         logger.error("请检查CloudFlare {} 账号下是否有 {} 域名".format(email, domain))
#         logger.error(traceback.format_exc())
#
#     except Exception as e:
#         logger.error("cloudflare_subdomains_record 未知异常")
#         logger.error(traceback.format_exc())
#
#     return False
#
#
# def delete_record(domain=None, key=None, email=None, sub_domain=None):
#     try:
#         top_domain = '.'.join(domain.split('.')[-2:])
#         base_url = "https://api.cloudflare.com/client/v4/zones"
#
#         headers = {
#             'Content-Type': 'application/json',
#             "X-Auth-Key": key,
#             "X-Auth-Email": email,
#         }
#         payload = {
#             "page": 1,
#             "per_page": 20,
#             "match": "all",
#         }
#
#         r = requests.get(base_url, headers=headers, params=payload, timeout=10)
#         status = r.json()["success"]
#         total_pages = r.json()["result_info"]["total_pages"]
#         result = r.json()["result"]
#
#         if not status:
#             logger.error("cloudflare请求失败")
#             logger.error(r.text)
#             return False
#
#         zone_id = None
#         page = 1
#         while page <= total_pages:
#             for item in result:
#                 if item["name"] == top_domain:
#                     zone_id = item["id"]
#                     break
#
#             page += 1
#             payload = {
#                 "page": page,
#                 "per_page": 20,
#                 "match": "all",
#             }
#
#             r = requests.get(base_url, headers=headers, params=payload, timeout=10)
#             result = r.json()["result"]
#
#         if not zone_id:
#             logger.error("没有查询%s 对应的 zone id" % domain)
#             return False
#
#         url = base_url + "/" + zone_id + "/" + "dns_records"
#         r = requests.get(url, headers=headers, timeout=10)
#         status = r.json()["success"]
#         result = r.json()["result"]
#
#         identifier = None
#         if status:
#             for item in result:
#                 if item["name"] == sub_domain + "." + top_domain:
#                     identifier = item["id"]
#                     break
#
#         if not identifier:
#             logger.error("没有查询到域名记录对应的id")
#             logger.error(r.text)
#             return False
#
#         url = base_url + "/" + zone_id + "/" + "dns_records" + "/" + identifier
#         r = requests.delete(url, headers=headers, timeout=10)
#         status = r.json()["success"]
#
#         if status:
#             logger.info(F"删除记录成功: {sub_domain}")
#             return True
#
#         logger.error("删除记录失败")
#         logger.error(r.text)
#         return False
#
#     except Exception as e:
#         logger.error("删除记录异常")
#         logger.error(traceback.format_exc())
#
#     return False
#
#
# def modify_record(domain=None, key=None, email=None, old_sub_domain=None, new_sub_domain=None, record_type=None,
#                   line=None, record_value=None, ttl=None, priority=None):
#     try:
#         top_domain = '.'.join(domain.split('.')[-2:])
#         base_url = "https://api.cloudflare.com/client/v4/zones"
#
#         headers = {
#             'Content-Type': 'application/json',
#             "X-Auth-Key": key,
#             "X-Auth-Email": email,
#         }
#         payload = {
#             "page": 1,
#             "per_page": 20,
#             "match": "all",
#         }
#
#         r = requests.get(base_url, headers=headers, params=payload, timeout=10)
#         status = r.json()["success"]
#         total_pages = r.json()["result_info"]["total_pages"]
#         result = r.json()["result"]
#
#         if not status:
#             logger.error("cloudflare请求失败")
#             logger.error(r.text)
#             return False
#
#         zone_id = None
#         page = 1
#         while page <= total_pages:
#             for item in result:
#                 if item["name"] == top_domain:
#                     zone_id = item["id"]
#                     break
#
#             page += 1
#             payload = {
#                 "page": page,
#                 "per_page": 20,
#                 "match": "all",
#             }
#
#             r = requests.get(base_url, headers=headers, params=payload, timeout=10)
#             result = r.json()["result"]
#
#         if not zone_id:
#             logger.error("没有查询%s 对应的 zone id" % domain)
#             return False
#
#         url = base_url + "/" + zone_id + "/" + "dns_records"
#         r = requests.get(url, headers=headers, timeout=10)
#         status = r.json()["success"]
#         result = r.json()["result"]
#
#         identifier = None
#         if status:
#             for item in result:
#                 if item["name"] == old_sub_domain + "." + top_domain:
#                     identifier = item["id"]
#                     break
#
#         if not identifier:
#             logger.error("没有查询到域名记录对应的id")
#             logger.error(r.text)
#             return False
#
#         url = base_url + "/" + zone_id + "/" + "dns_records" + "/" + identifier
#
#         if record_type == "显示URL" or record_type == "隐性URL":
#             record_type = "URI"
#
#         payload = {
#             "type": record_type,
#             "name": new_sub_domain + "." + top_domain,
#             "content": record_value,
#             # "ttl": 120 if int(ttl) < 120 else int(ttl),
#             "ttl": 1,  # 值为1，自动生效
#         }
#
#         if record_type == "MX":
#             payload.update({"priority": priority})
#
#         r = requests.put(url, headers=headers, data=json.dumps(payload), timeout=10)
#         status = r.json()["success"]
#
#         if status:
#             logger.info(F"修改记录成功: old_record: {old_sub_domain}  new_record: {new_sub_domain}")
#             return True
#
#         logger.error("修改记录失败")
#         logger.error(r.text)
#         return False
#
#     except Exception as e:
#         logger.error("修改记录状态异常")
#         logger.error(traceback.format_exc())
#
#     return False


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
                logger.error(F"No zone id was queried: {r.text}")

        except ConnectTimeout as e:
            logger.error(F"query zone id failed: {e}")
        except Exception:
            logger.error(F"query zone id unknown exception")
            logger.error(traceback.format_exc())

    def get_record_id(self, zone_id, sub_domain):
        """
        查询记录id
        :param zone_id:
        :param sub_domain:
        :return: id|None
        """
        try:
            dns_record_url = self.base_url + "/" + zone_id + "/" + "dns_records"
            r = requests.get(dns_record_url, headers=self.request_headers(), timeout=self.TIMEOUT)
            status = r.json()["success"]
            total_pages = r.json()["result_info"]["total_pages"]
            result = r.json()["result"]

            if not status:
                logger.error(F"query record failed: {r.text}")
                return None

            identifier = None
            for page in range(1, total_pages + 1):
                for item in result:
                    if item["name"] == sub_domain + "." + self.second_level_domain:
                        identifier = item["id"]
                        return identifier

                page += 1
                if page == total_pages + 1:
                    break

                r = requests.get(dns_record_url, headers=self.request_headers(), timeout=self.TIMEOUT)
                result = r.json()["result"]

            if not identifier:
                logger.error(F"record id was not queried: {r.text}")

        except ConnectTimeout as e:
            logger.error(F"get record id failed: {e}")
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
                    if item["name"] != self.domain and item["type"] not in ("MX", "TXT") and \
                            item["name"].endswith(self.domain):
                        data.append(
                            {
                                # "name": ".".join(item["name"].split(".")[0:-2]),
                                "name": item["name"],
                                "type": item["type"],
                                # "line": None,
                                "value": item["content"],
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
            logger.error(F"query sub domains failed: {e}")
        except Exception:
            logger.error(F"query sub domains unknown exception")
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
                        if item["name"] != self.domain and item["type"] not in ("MX", "TXT") and \
                                item["name"].endswith(self.domain):
                            data.append(
                                {
                                    # "name": ".".join(item["name"].split(".")[0:-2]),
                                    "name": item["name"],
                                    "type": item["type"],
                                    "line": None,
                                    "value": item["content"],
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
            logger.error(F"query sub domains failed: {e}")
        except Exception:
            logger.error(F"query sub domains unknown exception")
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

            logger.info(F"123: {payload}")

            if record_type == "MX":
                payload.update({"priority": priority})

            r = requests.post(add_record_url, headers=self.request_headers(), data=json.dumps(payload),
                              timeout=self.TIMEOUT)
            status = r.json()["success"]
            if status:
                logger.info(F"add record success: {sub_domain}")
                return True

            logger.error(F"add record failed: {r.text}")

        except ConnectTimeout as e:
            logger.error(F"add record failed: {sub_domain}")
        except UnboundLocalError as e:
            logger.error(F"Domain name under API account not found: [{self.key} : {self.email}]")
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
            logger.error(F"del record failed: {e}")
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
                "name": new_sub_domain + "." + self.second_level_domain,
                "content": record_value,
                "ttl": 1,  # 值为1，自动生效
            }

            if record_type == "MX":
                payload.update({"priority": priority})

            r = requests.put(modify_record_url, headers=self.request_headers(), data=json.dumps(payload), timeout=10)
            status = r.json()["success"]

            if status:
                logger.info(F"modify record success: [{old_sub_domain} -> {new_sub_domain}]")
                return True

            logger.error(F"modify record failed: {r.text}")

        except ConnectTimeout as e:
            logger.error(F"modify record failed: {e}")
        except Exception:
            logger.error("modify record unknown exception")
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    domain = ""
    account = {
        "key": "",
        "email": ""
    }

    sub_domain = "a1-test"
    # record_type = "CNAME"
    # record_value = "www.baidu.com"

    old_sub_domain = "test-blog"
    new_sub_domain = "aaa-blog"
    record_type = "A"
    record_value = "1.1.1.1"

    cloudflare = CLOUDFLARE(domain, account)
    ret = cloudflare.sub_domains()
    print(json.dumps(ret))
