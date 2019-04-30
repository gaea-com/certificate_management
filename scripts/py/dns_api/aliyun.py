# 单独执行py文件时，首先载入django环境
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certificate_management.settings')
django.setup()
#######
import logging
import json
import traceback
from cert_app.conf import dns_api_mode

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.SetDomainRecordStatusRequest import SetDomainRecordStatusRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DeleteSubDomainRecordsRequest import DeleteSubDomainRecordsRequest

# aliyun查询子域名接口
logger = logging.getLogger('django')


# def sub_domains(domain=None, key=None, secret=None):
#     """
#     返回所有子域名列表
#     :param domain: str
#     :param key: str
#     :param secret: str
#     :return: list
#     """
#     try:
#         if domain.endswith(".com.cn") or \
#                 domain.endswith(".net.cn") or \
#                 domain.endswith(".org.cn") or \
#                 domain.endswith(".gov.cn"):
#             domain_ext = '.'.join(domain.split(".")[0:-3])
#             top_level_domain = '.'.join(domain.split('.')[-3:])
#         else:
#             domain_ext = '.'.join(domain.split(".")[0:-2])
#             top_level_domain = '.'.join(domain.split('.')[-2:])
#
#         client = AcsClient(key, secret, 'cn-hangzhou')
#
#         request = DescribeDomainRecordsRequest()
#         request.set_accept_format('json')
#
#         request.set_PageSize(500)  # 分页查询时设置的每页行数，最大值500，默认为20
#         request.set_DomainName(top_level_domain)
#
#         response = client.do_action_with_exception(request)
#
#         response = json.loads(response)
#         records = response["DomainRecords"]["Record"]
#
#         subdomains = []
#         for item in records:
#             if item["RR"] not in ("@", "*", domain_ext) and item["Type"] != "TXT" and item["RR"].endswith(domain_ext):
#                 subdomains.append(
#                     {
#                         "sub_domain": item["RR"] + "." + item["DomainName"],
#                         "record_type": item["Type"],
#                         "record_value": item["Value"]
#                     }
#                 )
#
#         # logger.info("阿里云子域名列表: {}".format(subdomains))
#         return subdomains
#
#     except KeyError as e:
#         logger.error("该域名不存在: {}".format(domain))
#         logger.error(traceback.format_exc())
#
#     except Exception as e:
#         logger.error("阿里云子域名查询未知异常")
#         logger.error(traceback.format_exc())
#
#     return []
#
#
# def get_all_sub_domain(domain=None, key=None, secret=None):
#     """
#     返回所有子域名列表
#     :param domain: str
#     :param key: str
#     :param secret: str
#     :return: list
#     """
#     try:
#         line = {
#             "default": "默认",
#             "telecom": "电信",
#             "unicom": "联通",
#             "mobile": "移动",
#             "oversea": "海外",
#         }
#
#         if domain.endswith(".com.cn") or \
#                 domain.endswith(".net.cn") or \
#                 domain.endswith(".org.cn") or \
#                 domain.endswith(".gov.cn"):
#             top_level_domain = '.'.join(domain.split('.')[-3:])
#         else:
#             top_level_domain = '.'.join(domain.split('.')[-2:])
#
#         client = AcsClient(key, secret, 'cn-hangzhou')
#
#         request = DescribeDomainRecordsRequest()
#         request.set_accept_format('json')
#
#         request.set_PageSize(500)  # 分页查询时设置的每页行数，最大值500，默认为20
#         request.set_DomainName(top_level_domain)
#
#         response = client.do_action_with_exception(request)
#
#         response = json.loads(response)
#         records = response["DomainRecords"]["Record"]
#         if records:
#             logger.info("查询所有子域名")
#
#             data = []
#             for item in records:
#                 data.append(
#                     {
#                         "name": item["RR"],
#                         "type": item["Type"],
#                         "line": line[item["Line"]],
#                         "value": item["Value"],
#                         "ttl": item["TTL"],
#                         "status": "正常" if item["Status"] == "ENABLE" else "暂停",  # ENABLE DISABLE
#                     }
#                 )
#             return data
#
#         logger.error(response)
#
#     except KeyError as e:
#         logger.error("该域名不存在: {}".format(domain))
#         logger.error(traceback.format_exc())
#
#     except Exception as e:
#         logger.error("阿里云子域名查询未知异常")
#         logger.error(traceback.format_exc())
#
#     return []
#
#
# def record_line(value):
#     """
#     基础线路
#     线路值	线路中文说明
#     default	默认
#     telecom	电信
#     unicom	联通
#     mobile	移动
#     oversea	海外
#     edu	教育网
#     drpeng	鹏博士
#     btvn	广电网
#     """
#     line = {
#         "default": "默认",
#         "telecom": "电信",
#         "unicom": "联通",
#         "mobile": "移动",
#         "oversea": "海外",
#     }
#
#     if value == "国外":
#         value = "海外"
#
#     for k, v in line.items():
#         if v == value:
#             return k
#
#     return None
#
#
# def add_record(domain=None, key=None, secret=None, RR=None, Type=None, Line=None, Value=None, TTL=None, MX=None):
#     """
#     返回所有子域名列表
#     :param domain: str
#     :param key: str
#     :param secret: str
#     :return: list
#     """
#     try:
#         if domain.endswith(".com.cn") or \
#                 domain.endswith(".net.cn") or \
#                 domain.endswith(".org.cn") or \
#                 domain.endswith(".gov.cn"):
#             top_level_domain = '.'.join(domain.split('.')[-3:])
#         else:
#             top_level_domain = '.'.join(domain.split('.')[-2:])
#
#         if Type == "显示URL":
#             Type = "REDIRECT_URL"
#
#         if Type == "隐性URL":
#             Type = "FORWARD_URL"
#
#         client = AcsClient(key, secret, 'cn-hangzhou')
#
#         request = AddDomainRecordRequest()
#         request.set_accept_format('json')
#
#         request.set_Line(record_line(Line))
#         request.set_TTL(600 if int(TTL) < 600 else int(TTL))
#         request.set_Value(Value)
#         request.set_Type(Type)
#         request.set_RR(RR)
#         request.set_DomainName(top_level_domain)
#
#         if Type == "MX":
#             request.set_Priority(MX)
#
#         response = client.do_action_with_exception(request)
#         response = json.loads(response)
#
#         if "Code" in response.keys():
#             logger.error(F"添加域名 {top_level_domain} 记录失败 {RR}")
#             logger.error(response)
#             return False
#
#         return True
#
#     except Exception as e:
#         logger.error("添加记录未知异常")
#         logger.error(traceback.format_exc())
#
#     return False
#
#
# def delete_record(domain=None, key=None, secret=None, RR=None):
#     if domain.endswith(".com.cn") or \
#             domain.endswith(".net.cn") or \
#             domain.endswith(".org.cn") or \
#             domain.endswith(".gov.cn"):
#         top_domain = '.'.join(domain.split('.')[-3:])
#     else:
#         top_domain = '.'.join(domain.split('.')[-2:])
#
#     client = AcsClient(key, secret, 'cn-hangzhou')
#
#     request = DeleteSubDomainRecordsRequest()
#     request.set_accept_format('json')
#
#     request.set_RR(RR)
#     request.set_DomainName(top_domain)
#
#     response = client.do_action_with_exception(request)
#     # print(str(response, encoding='utf-8'))
#     response = json.loads(response)
#     totalCount = response["TotalCount"]
#
#     if totalCount == "1":
#         logger.info(F"删除记录成功: {RR}")
#         return True
#
#     logger.error("删除域名记录失败")
#     logger.error(response)
#     return False
#
#
# def set_record_status(domain=None, key=None, secret=None, RR=None, status=None):
#     """status: Enable Disable"""
#
#     if domain.endswith(".com.cn") or \
#             domain.endswith(".net.cn") or \
#             domain.endswith(".org.cn") or \
#             domain.endswith(".gov.cn"):
#         top_domain = '.'.join(domain.split('.')[-3:])
#     else:
#         top_domain = '.'.join(domain.split('.')[-2:])
#
#     client = AcsClient(key, secret, 'cn-hangzhou')
#
#     request = DescribeDomainRecordsRequest()
#     request.set_accept_format('json')
#
#     request.set_DomainName(top_domain)
#
#     response = client.do_action_with_exception(request)
#     response = json.loads(response)
#
#     records = response["DomainRecords"]["Record"]
#
#     record_id = "".join([item["RecordId"] for item in records if item["RR"] == RR])
#     if not record_id:
#         logger.error("没有查询到record id")
#         logger.error(response)
#         return False
#
#     request = SetDomainRecordStatusRequest()
#     request.set_accept_format('json')
#
#     request.set_Status(status.capitalize())
#     request.set_RecordId(record_id)
#
#     response = client.do_action_with_exception(request)
#     response = json.loads(response)
#
#     if response["Status"] == "Disable":
#         logger.info(F"{RR} 记录已禁用")
#         return True
#     elif response["Status"] == "Enable":
#         logger.info(F"{RR} 记录已启用")
#         return True
#
#     logger.error(F"禁用 {RR} 失败")
#     logger.error(response)
#     return False
#
#
# def modify_record(domain=None, key=None, secret=None, old_RR=None, new_RR=None, Type=None, Line=None, Value=None,
#                   TTL=None, MX=None):
#     if domain.endswith(".com.cn") or \
#             domain.endswith(".net.cn") or \
#             domain.endswith(".org.cn") or \
#             domain.endswith(".gov.cn"):
#         top_domain = '.'.join(domain.split('.')[-3:])
#     else:
#         top_domain = '.'.join(domain.split('.')[-2:])
#
#     client = AcsClient(key, secret, 'cn-hangzhou')
#
#     request = DescribeDomainRecordsRequest()
#     request.set_accept_format('json')
#
#     request.set_DomainName(top_domain)
#
#     response = client.do_action_with_exception(request)
#     response = json.loads(response)
#
#     records = response["DomainRecords"]["Record"]
#
#     record_id = "".join([item["RecordId"] for item in records if item["RR"] == old_RR])
#     if not record_id:
#         logger.error("没有查询到record id")
#         logger.error(response)
#         return False
#
#     if Type == "显示URL":
#         Type = "REDIRECT_URL"
#
#     if Type == "隐性URL":
#         Type = "FORWARD_URL"
#
#     request = UpdateDomainRecordRequest()
#     request.set_accept_format('json')
#     request.set_Line(record_line(Line))
#     request.set_TTL(600 if int(TTL) < 600 else int(TTL))
#     request.set_Value(Value)
#     request.set_Type(Type)
#     request.set_RR(new_RR)
#     request.set_RecordId(record_id)
#
#     if Type == "MX":
#         request.set_Priority(MX)
#
#     try:
#         response = client.do_action_with_exception(request)
#         response = json.loads(response)
#
#         if "Code" in response.keys():
#             logger.error(F"修改 {domain} 记录失败: {new_RR}")
#             logger.error(response)
#             return False
#
#         logger.info(F"修改记录成功: old_record: {old_RR}  new_record: {new_RR}")
#         return True
#     except ServerException as e:
#         logger.warning("记录没有作任何修改")
#         logger.warning(e)
#         return True


class ALIYUN(object):
    def __init__(self, domain, account):
        self.key = account[dns_api_mode["aliyun"][0]]
        self.secret = account[dns_api_mode["aliyun"][1]]
        # self.TIMEOUT = 10

        if domain.endswith(".com.cn") or \
                domain.endswith(".net.cn") or \
                domain.endswith(".org.cn") or \
                domain.endswith(".gov.cn"):
            self.prefix_domain = '.'.join(domain.split(".")[0:-3])
            self.second_level_domain = '.'.join(domain.split('.')[-3:])
        else:
            self.prefix_domain = '.'.join(domain.split(".")[0:-2])
            self.second_level_domain = '.'.join(domain.split('.')[-2:])

    def record_line(self, key=None, value=None):
        """
            基础线路
            线路值	线路中文说明
            default	默认
            telecom	电信
            unicom	联通
            mobile	移动
            oversea	海外
            edu	教育网
            drpeng	鹏博士
            btvn	广电网
        """

        line = {
            "default": "默认",
            "telecom": "电信",
            "unicom": "联通",
            "mobile": "移动",
            "oversea": "海外",
        }

        if key:
            return line[key]

        if value == "国外":
            value = "海外"

        for k, v in line.items():
            if v == value:
                return k

    def get_record_id(self, RR):
        """
        查询record id
        :return: id|None
        """
        try:
            client = AcsClient(self.key, self.secret, 'cn-hangzhou')
            request = DescribeDomainRecordsRequest()
            request.set_accept_format('json')
            request.set_DomainName(self.second_level_domain)
            response = client.do_action_with_exception(request)

            response = json.loads(response)
            records = response["DomainRecords"]["Record"]

            record_id = "".join([item["RecordId"] for item in records if item["RR"] == RR])

            if record_id:
                return record_id

            logger.error(F"not found record id: {response}")

        except Exception:
            logger.error("query record id unknown exception")
            logger.error(traceback.format_exc())

    def part_sub_domains(self):
        """
        查询所有子域名
        :return: list|None
        """
        try:
            client = AcsClient(self.key, self.secret, 'cn-hangzhou')
            request = DescribeDomainRecordsRequest()
            request.set_accept_format('json')
            request.set_PageSize(500)  # 分页查询时设置的每页行数，最大值500，默认为20
            request.set_DomainName(self.second_level_domain)
            response = client.do_action_with_exception(request)

            response = json.loads(response)
            records = response["DomainRecords"]["Record"]

            if not records:
                logger.error(F"query sub domains failed: {response}")
                return None

            data = []
            for item in records:
                if item["RR"] != self.prefix_domain and item["Type"] not in ("MX", "TXT") and item["RR"].endswith(
                        self.prefix_domain):
                    data.append(
                        {
                            "name": item["RR"] + "." + item["DomainName"],
                            "type": item["Type"],
                            # "line": self.record_line(key=item["Line"]),
                            "value": item["Value"],
                            # "ttl": item["TTL"],
                            # "status": "正常" if item["Status"] == "ENABLE" else "暂停",  # ENABLE DISABLE
                        }
                    )
            return data

        except KeyError as e:
            logger.error(F"domain not exist: {e}")

        except Exception:
            logger.error("query sub domains unknown exception")
            logger.error(traceback.format_exc())

    def sub_domains(self, part=None):
        """
        查询所有子域名
        :return: list|None
        """
        try:
            client = AcsClient(self.key, self.secret, 'cn-hangzhou')
            request = DescribeDomainRecordsRequest()
            request.set_accept_format('json')
            request.set_PageSize(500)  # 分页查询时设置的每页行数，最大值500，默认为20
            request.set_DomainName(self.second_level_domain)
            response = client.do_action_with_exception(request)

            response = json.loads(response)
            records = response["DomainRecords"]["Record"]

            if not records:
                logger.error(F"query sub domains failed: {response}")
                return None

            data = []
            for item in records:
                if part:
                    if item["RR"] != self.prefix_domain and item["Type"] not in ("MX", "TXT") and item["RR"].endswith(
                            self.prefix_domain):
                        data.append(
                            {
                                "name": item["RR"] + "." + self.second_level_domain,
                                "type": item["Type"],
                                "line": self.record_line(key=item["Line"]),
                                "value": item["Value"],
                                "ttl": item["TTL"],
                                "status": "正常" if item["Status"] == "ENABLE" else "暂停",  # ENABLE DISABLE
                            }
                        )
                else:
                    data.append(
                        {
                            "name": item["RR"] + "." + self.second_level_domain,
                            "type": item["Type"],
                            "line": self.record_line(key=item["Line"]),
                            "value": item["Value"],
                            "ttl": item["TTL"],
                            "status": "正常" if item["Status"] == "ENABLE" else "暂停",  # ENABLE DISABLE
                        }
                    )
            return data

        except KeyError as e:
            logger.error(F"domain not exist: {e}")

        except Exception:
            logger.error("query sub domains unknown exception")
            logger.error(traceback.format_exc())

    def add_record(self, RR=None, Type=None, Line=None, Value=None, TTL=None, MX=None):
        """
        添加记录
        :return: True|False
        """
        try:
            if Type == "显示URL":
                Type = "REDIRECT_URL"

            if Type == "隐性URL":
                Type = "FORWARD_URL"

            client = AcsClient(self.key, self.secret, 'cn-hangzhou')
            request = AddDomainRecordRequest()
            request.set_accept_format('json')
            request.set_Line(self.record_line(value=Line))
            request.set_TTL(600 if int(TTL) < 600 else int(TTL))
            request.set_Value(Value)
            request.set_Type(Type)
            request.set_RR(RR + ("." + self.prefix_domain if self.prefix_domain else ""))
            request.set_DomainName(self.second_level_domain)

            if Type == "MX":
                request.set_Priority(MX)

            response = client.do_action_with_exception(request)
            response = json.loads(response)

            if "Code" in response.keys():
                logger.error(F"add record failed: {response}")
                return False

            logger.info(F"add record success: {RR}")
            return True

        except Exception:
            logger.error("add record unknown exception")
            logger.error(traceback.format_exc())
            return False

    def delete_record(self, RR=None):
        """
        删除记录
        :return: True|False
        """
        try:
            client = AcsClient(self.key, self.secret, 'cn-hangzhou')
            request = DeleteSubDomainRecordsRequest()
            request.set_accept_format('json')
            request.set_RR(RR)
            request.set_DomainName(self.second_level_domain)

            response = client.do_action_with_exception(request)
            # print(str(response, encoding='utf-8'))
            response = json.loads(response)
            totalCount = response["TotalCount"]

            if totalCount == "1":
                logger.info(F"delete record success: {RR}")
                return True

            logger.error(F"delete record failed: {response}")

        except Exception:
            logger.error("delete record unknown exception")
            logger.error(traceback.format_exc())

        return False

    def set_record_status(self, RR=None, status=None):
        """
        修改记录状态
        status {enable|disable}
        :return: True|False
        """
        try:
            if self.get_record_id(RR):
                record_id = self.get_record_id(RR)
            else:
                return False

            client = AcsClient(self.key, self.secret, 'cn-hangzhou')
            request = SetDomainRecordStatusRequest()
            request.set_accept_format('json')
            request.set_Status(status.capitalize())
            request.set_RecordId(record_id)
            response = client.do_action_with_exception(request)
            response = json.loads(response)

            if response["Status"] == "Disable":
                logger.info(F"set record status: [{RR} : Disable]")
                return True
            elif response["Status"] == "Enable":
                logger.info(F"set record status: [{RR} : Enable]")
                return True

            logger.error(F"set record status failed: {response}")
            return False

        except Exception:
            logger.error("set record status unknown exception")
            logger.error(traceback.format_exc())
            return False

    def modify_record(self, old_RR=None, new_RR=None, Type=None, Line=None, Value=None,
                      TTL=None, MX=None):
        """
        修改记录
        :return: True|False
        """
        try:
            if self.get_record_id(old_RR):
                record_id = self.get_record_id(old_RR)
            else:
                return False

            if Type == "显示URL":
                Type = "REDIRECT_URL"

            if Type == "隐性URL":
                Type = "FORWARD_URL"

            client = AcsClient(self.key, self.secret, 'cn-hangzhou')
            request = UpdateDomainRecordRequest()
            request.set_accept_format('json')
            request.set_Line(self.record_line(value=Line))
            request.set_TTL(600 if int(TTL) < 600 else int(TTL))
            request.set_Value(Value)
            request.set_Type(Type)
            request.set_RR(new_RR)
            request.set_RecordId(record_id)

            if Type == "MX":
                request.set_Priority(MX)

            try:
                response = client.do_action_with_exception(request)
                response = json.loads(response)

                if "Code" in response.keys():
                    logger.error(F"modify record failed: {response}")
                    logger.error(response)
                    return False

                logger.info(F"modify record success: [{old_RR} -> {new_RR}]")
                return True

            except ServerException as e:
                logger.warning(F"No changes for record: {e}")
                return True

        except Exception:
            logger.error(F"modify record unknown exception")
            logger.error(traceback.format_exc())
            return False


if __name__ == "__main__":
    domain = ""
    account = {
        "key": "",
        "secret": ""
    }

    RR = "testaaa-fdsafds"
    Type = "A"
    Line = "默认"
    Value = "11.1.1.1"
    TTL = 600
    status = "Enable"

    old_RR = "testaaa-fdsafds"
    new_RR = "a2-test"

    # aliyun = ALIYUN(domain, account)
    # ret = aliyun.modify_record(old_RR, new_RR, Type, Line, Value, TTL)
    # print(json.dumps(ret))
