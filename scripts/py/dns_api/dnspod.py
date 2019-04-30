import logging
import requests
import traceback
import json
from requests.exceptions import ConnectTimeout
from cert_app.conf import dns_api_mode

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


# def sub_domains(domain=None, id_=None, key=None):
#     """
#     返回当前域名的子域名列表
#     :param domain: str
#     :param id_: str
#     :param key: str
#     :return: list
#     """
#     try:
#         domain_ext = '.'.join(domain.split(".")[0:-2])
#         domain = '.'.join(domain.split('.')[-2:])
#
#         record_list_url = "https://dnsapi.cn/Record.List"
#         payload = {
#             "login_token": "{},{}".format(id_, key),  # id_ 和 key以逗号分割
#             "format": "json",
#             "domain": domain,
#             "offset": 0,
#             "length": 100,
#         }
#
#         r = requests.post(record_list_url, data=payload, timeout=10)
#         code = r.json()["status"]["code"]
#
#         if code == "1":
#             subdomains = []
#             records = r.json()['records']
#
#             for record in records:
#                 if record['name'] not in ("@", "*", domain_ext) and record["type"] != "TXT" and record['name'].endswith(
#                         domain_ext):
#                     subdomains.append(
#                         {
#                             "sub_domain": record['name'] + "." + domain,
#                             "record_type": record['type'],
#                             "record_value": record['value']
#                         }
#                     )
#
#             # logger.info("DnsPod子域名列表: {}".format(subdomains))
#             return subdomains
#
#         logger.error("获取子域名失败: {}".format(r.text))
#
#     except Exception as e:
#         logger.error("获取子域名未知异常")
#         logger.error(traceback.format_exc())
#
#     return []
#
#
# def get_all_sub_domain(domain=None, id_=None, key=None):
#     """
#     查询顶级域名下的所有子域名
#     :param domain: str
#     :param id_: str
#     :param key: str
#     :return: list
#     """
#     try:
#         domain = '.'.join(domain.split('.')[-2:])
#
#         record_list_url = "https://dnsapi.cn/Record.List"
#
#         payload = {
#             "login_token": "{},{}".format(id_, key),  # id_ 和 key以逗号分割
#             "format": "json",
#             "domain": domain,
#             "offset": 0,
#             "length": 100,
#         }
#
#         r = requests.post(record_list_url, data=payload, timeout=10)
#         code = r.json()["status"]["code"]
#
#         if code == "1":
#             logger.info("查询所有子域名")
#             records = r.json()['records']
#
#             data = []
#             for item in records:
#                 data.append(
#                     {
#                         "name": item["name"],
#                         "type": item["type"],
#                         "line": item["line"],
#                         "value": item["value"],
#                         "ttl": item["ttl"],
#                         "status": "正常" if item["enabled"] == "1" else "暂停",
#                     }
#                 )
#             return data
#
#         logger.error(F"获取顶级下的子域名失败: {r.json()['status']}")
#
#     except Exception as e:
#         logger.error("获取顶级下的子域名未知异常")
#         logger.error(traceback.format_exc())
#
#     return []
#
#
# def add_record(domain=None, id_=None, key=None, sub_domain=None, record_type=None, record_line=None, value=None,
#                ttl=None, mx=None):
#     """
#     查询顶级域名下的所有子域名
#     :param domain:
#     :param id_:
#     :param key:
#     :param sub_domain:
#     :param record_type:
#     :param record_line:
#     :param value:
#     :param ttl:
#     :param mx:
#     :return: True/False
#
#
#     "types": [
#         "A",
#         "CNAME",
#         "MX",
#         "TXT",
#         "NS",
#         "AAAA",
#         "SRV",
#         "URL"
#     ]
#     "line_ids": {
#         "默认": 0,
#         "国内": "7=0",
#         "国外": "3=0",
#         "电信": "10=0",
#         "联通": "10=1",
#         "教育网": "10=2",
#         "移动": "10=3",
#         "百度": "90=0",
#         "谷歌": "90=1",
#         "搜搜": "90=4",
#         "有道": "90=2",
#         "必应": "90=3",
#         "搜狗": "90=5",
#         "奇虎": "90=6",
#         "搜索引擎": "80=0"
#     },
#     "lines": [
#         "默认",
#         "国内",
#         "国外",
#         "电信",
#         "联通",
#         "教育网",
#         "移动",
#         "百度",
#         "谷歌",
#         "搜搜",
#         "有道",
#         "必应",
#         "搜狗",
#         "奇虎",
#         "搜索引擎"
#     ]
#     """
#     try:
#         domain = '.'.join(domain.split('.')[-2:])
#
#         record_list_url = "https://dnsapi.cn/Record.Create"
#
#         if record_type == "显示URL" or record_type == "隐性URL":
#             record_type = "URL"
#
#         payload = {
#             "login_token": "{},{}".format(id_, key),  # id_ 和 key以逗号分割
#             "format": "json",
#             "domain": domain,
#             "sub_domain": sub_domain,
#             "record_type": record_type.upper(),
#             "record_line": record_line,
#             "value": value,
#             "ttl": 600 if int(ttl) < 600 else int(ttl),
#         }
#
#         if record_type == "MX":
#             payload.update({"mx": mx})
#
#         r = requests.post(record_list_url, data=payload, timeout=10)
#         code = r.json()["status"]["code"]
#
#         if code == "1":
#             logger.info(F"添加记录成功: {sub_domain}")
#             return True
#
#         logger.error(F"添加记录失败: {r.json()['status']}")
#
#     except Exception as e:
#         logger.error("添加记录未知异常")
#         logger.error(traceback.format_exc())
#
#     return False
#
#
# def delete_record(domain=None, id_=None, key=None, sub_domain=None):
#     try:
#         domain = '.'.join(domain.split('.')[-2:])
#
#         url = "https://dnsapi.cn/Record.List"
#         payload = {
#             "login_token": "{},{}".format(id_, key),  # id_ 和 key以逗号分割
#             "format": "json",
#             "domain": domain,
#             "offset": 0,
#             "length": 100,
#         }
#
#         r = requests.post(url, data=payload, timeout=10)
#         code = r.json()["status"]["code"]
#
#         record_id = ""
#         if code == "1":
#             records = r.json()['records']
#             for record in records:
#                 if record["name"] == sub_domain:
#                     record_id = record["id"]
#
#             if not record_id:
#                 logger.error(F"没有查询到 {sub_domain} 的记录ID")
#                 return False
#
#         url = "https://dnsapi.cn/Record.Remove"
#         payload = {
#             "login_token": "{},{}".format(id_, key),  # id_ 和 key以逗号分割
#             "format": "json",
#             "domain": domain,
#             "record_id": record_id,
#         }
#         r = requests.post(url, data=payload, timeout=10)
#         code = r.json()["status"]["code"]
#         if code == "1":
#             logger.info(F"删除记录成功: {sub_domain}")
#             return True
#
#         logger.error(F"删除记录失败: {sub_domain}")
#
#     except Exception as e:
#         logger.error("删除记录异常")
#         logger.error(traceback.format_exc())
#
#     return False
#
#
# def set_record_status(domain=None, id_=None, key=None, sub_domain=None, status=None):
#     try:
#         domain = '.'.join(domain.split('.')[-2:])
#
#         url = "https://dnsapi.cn/Record.List"
#         payload = {
#             "login_token": "{},{}".format(id_, key),  # id_ 和 key以逗号分割
#             "format": "json",
#             "domain": domain,
#             "offset": 0,
#             "length": 100,
#         }
#
#         r = requests.post(url, data=payload, timeout=10)
#         code = r.json()["status"]["code"]
#
#         record_id = ""
#         if code == "1":
#             records = r.json()['records']
#             for record in records:
#                 if record["name"] == sub_domain:
#                     record_id = record["id"]
#
#             if not record_id:
#                 logger.error(F"没有查询到 {sub_domain} 的记录ID")
#                 return False
#
#         url = "https://dnsapi.cn/Record.Status"
#         payload = {
#             "login_token": "{},{}".format(id_, key),  # id_ 和 key以逗号分割
#             "format": "json",
#             "domain": domain,
#             "record_id": record_id,
#             "status": status.lower(),
#         }
#         r = requests.post(url, data=payload, timeout=10)
#         code = r.json()["status"]["code"]
#         if code == "1":
#             logger.info(F"{sub_domain} 记录状态已设置为 {status}")
#             return True
#
#         logger.error(F"更新记录状态失败: {sub_domain}")
#
#     except Exception as e:
#         logger.error("更新记录状态异常")
#         logger.error(traceback.format_exc())
#
#     return False
#
#
# def modify_record(domain=None, id_=None, key=None, old_sub_domain=None, new_sub_domain=None, record_type=None,
#                   record_line=None, value=None, ttl=None, mx=None):
#     try:
#         domain = '.'.join(domain.split('.')[-2:])
#
#         url = "https://dnsapi.cn/Record.List"
#         payload = {
#             "login_token": "{},{}".format(id_, key),  # id_ 和 key以逗号分割
#             "format": "json",
#             "domain": domain,
#             "offset": 0,
#             "length": 100,
#         }
#
#         r = requests.post(url, data=payload, timeout=10)
#         code = r.json()["status"]["code"]
#
#         record_id = None
#         if code != "1":
#             logger.error("请求失败")
#             logger.error(r.text)
#             return False
#
#         records = r.json()['records']
#         for record in records:
#             if record["name"] == old_sub_domain:
#                 record_id = record["id"]
#
#         if not record_id:
#             logger.error(F"没有查询到 {old_sub_domain} 的记录ID")
#             return False
#
#         url = "https://dnsapi.cn/Record.Modify"
#
#         if record_type == "显示URL" or record_type == "隐性URL":
#             record_type = "URL"
#
#         payload = {
#             "login_token": "{},{}".format(id_, key),  # id_ 和 key以逗号分割
#             "format": "json",
#             "domain": domain,
#             "record_id": record_id,
#             "sub_domain": new_sub_domain,
#             "record_type": record_type.upper(),
#             "record_line": record_line,
#             "value": value,
#             "ttl": 600 if int(ttl) < 600 else int(ttl),
#         }
#
#         if record_type == "MX":
#             payload.update({"mx": mx})
#
#         r = requests.post(url, data=payload, timeout=10)
#         code = r.json()["status"]["code"]
#         if code == "1":
#             logger.info(F"修改记录成功: old_record: {old_sub_domain}  new_record: {new_sub_domain}")
#             return True
#
#         logger.error(F"修改记录失败: {new_sub_domain}")
#         logger.error(r.text)
#
#     except Exception as e:
#         logger.error("修改记录异常")
#         logger.error(traceback.format_exc())
#
#     return False


class DNSPOD(object):
    def __init__(self, domain, account):
        # self.domain = domain
        self.id_ = account[dns_api_mode["dnspod"][0]]
        self.key = account[dns_api_mode["dnspod"][1]]
        self.TIMEOUT = 10

        if domain.endswith(".com.cn") or \
                domain.endswith(".net.cn") or \
                domain.endswith(".ac.cn"):
            self.prefix_domain = '.'.join(domain.split(".")[0:-3])
            self.second_level_domain = '.'.join(domain.split('.')[-3:])
        else:
            self.prefix_domain = '.'.join(domain.split(".")[0:-2])
            self.second_level_domain = '.'.join(domain.split('.')[-2:])

    def record_list(self):
        """
        查询域名所有的记录
        :return: list
        """
        try:
            URL = "https://dnsapi.cn/Record.List"
            payload = {
                "login_token": "{},{}".format(self.id_, self.key),  # id_ 和 key以逗号分割
                "format": "json",
                "domain": self.second_level_domain,
                "offset": 0,
                "length": 100,
            }

            r = requests.post(URL, data=payload, timeout=self.TIMEOUT)
            code = r.json()["status"]["code"]

            if code == "1":
                return r
            else:
                logger.error(F"query record list failed: {r.text}")

        except ConnectTimeout as e:
            logger.error(F"query record failed: {self.second_level_domain}")
        except Exception:
            logger.error("query record unknown exception")
            logger.error(traceback.format_exc())

    def record_id(self, sub_domain):
        """
        查询记录对应的id
        :return: id
        """
        if self.record_list():
            records = self.record_list().json()['records']

            record_id = None
            for record in records:
                if record["name"] == sub_domain:
                    record_id = record["id"]

            if record_id:
                return record_id

            logger.error(F"No record ID was queried: {sub_domain}")

    def part_sub_domains(self):
        """
        统一所有记录的存储格式
        :return: dict
        """
        if self.record_list():
            records = self.record_list().json()['records']

            data = []
            for item in records:
                # 过滤掉 MX TXT类型的记录
                # if item["type"] in ("MX", "TXT"):
                #     continue
                if item['name'] != self.prefix_domain and item["type"] not in ("MX", "TXT") \
                        and item['name'].endswith(self.prefix_domain):
                    data.append(
                        {
                            "name": item["name"] + "." + self.second_level_domain,
                            "type": item["type"],
                            # "line": item["line"],
                            "value": item["value"],
                            # "ttl": item["ttl"],
                            # "status": "正常" if item["enabled"] == "1" else "暂停",
                        }
                    )

            return data

    def sub_domains(self, part=None):
        """
        统一所有记录的存储格式
        :return: dict
        """
        if self.record_list():
            records = self.record_list().json()['records']

            data = []
            for item in records:
                # 过滤掉 MX TXT类型的记录
                # if item["type"] in ("MX", "TXT"):
                #     continue
                if part:
                    if item['name'] != self.prefix_domain and item["type"] not in ("MX", "TXT") \
                            and item['name'].endswith(self.prefix_domain):
                        data.append(
                            {
                                "name": item["name"] + "." + self.second_level_domain,
                                "type": item["type"],
                                "line": item["line"],
                                "value": item["value"],
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
                            "ttl": item["ttl"],
                            "status": "正常" if item["enabled"] == "1" else "暂停",
                        }
                    )

            return data

    def add_record(self, sub_domain=None, record_type=None, record_line=None, value=None, ttl=None, mx=None):
        """
        添加记录
        :return: True|False
        """
        try:
            URL = "https://dnsapi.cn/Record.Create"
            if record_type == "显示URL" or record_type == "隐性URL":
                record_type = "URL"

            payload = {
                "login_token": "{},{}".format(self.id_, self.key),  # id_ 和 key以逗号分割
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

    def delete_record(self, sub_domain=None):
        """
        删除记录
        :return: True|False
        """
        try:
            if not self.record_id(sub_domain):
                return False

            record_id = self.record_id(sub_domain)

            URL = "https://dnsapi.cn/Record.Remove"
            payload = {
                "login_token": "{},{}".format(self.id_, self.key),  # id_ 和 key以逗号分割
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
            logger.error(F"del record failed: {e}")
        except Exception:
            logger.error("del record unknown exception")
            logger.error(traceback.format_exc())

    def set_record_status(self, sub_domain=None, status=None):
        """
        设置记录的状态
        status {enable|disable}
        :return: True|False
        """
        try:
            if not self.record_id(sub_domain):
                return False
            record_id = self.record_id(sub_domain)

            URL = "https://dnsapi.cn/Record.Status"
            payload = {
                "login_token": "{},{}".format(self.id_, self.key),  # id_ 和 key以逗号分割
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
            logger.error(F"set record status failed: {e}")
        except Exception:
            logger.error("set record unknown exception")
            logger.error(traceback.format_exc())

    def modify_record(self, old_sub_domain=None, new_sub_domain=None, record_type=None, record_line=None, value=None,
                      ttl=None, mx=None):
        """
        修改记录
        :return: True|False
        """
        try:
            if not self.record_id(old_sub_domain):
                return False

            record_id = self.record_id(old_sub_domain)

            URL = "https://dnsapi.cn/Record.Modify"

            if record_type == "显示URL" or record_type == "隐性URL":
                record_type = "URL"

            payload = {
                "login_token": "{},{}".format(self.id_, self.key),  # id_ 和 key以逗号分割
                "format": "json",
                "domain": self.second_level_domain,
                "record_id": record_id,
                "sub_domain": new_sub_domain,
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
        "id": "",
        "key": "",
    }
    sub_domain = "rrrrfff"
    record_type = "A"
    record_line = "默认"
    value = "1.1.1.1"
    ttl = 600
    status = "enable"

    old_sub_domain = "fff"
    new_sub_domain = "a2-test"
    dnspod = DNSPOD(domain, account)

    print(dnspod.record_list())
