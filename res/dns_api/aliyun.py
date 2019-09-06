import logging
import json
import traceback
from apps.ssl_cert.config import dns_api_mode

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.SetDomainRecordStatusRequest import SetDomainRecordStatusRequest
from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
from aliyunsdkalidns.request.v20150109.DeleteSubDomainRecordsRequest import DeleteSubDomainRecordsRequest

# aliyun查询子域名接口
logger = logging.getLogger('django')


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

    def get_record_id(self, rr):
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

            if self.prefix_domain:
                rr = ''.join([rr, ".", self.prefix_domain])
            record_id = "".join([item["RecordId"] for item in records if item["RR"] == rr])

            if record_id:
                return record_id

            logger.error(F"cat not get record id: {response}")

        except Exception:
            logger.error("get record id unknown exception")
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
                if item["RR"] != self.prefix_domain and item["Type"] not in ("MX", "TXT", "SRV", "NS") and \
                        item["RR"].endswith(self.prefix_domain):
                    data.append(
                        {
                            "name": item["RR"] + "." + item["DomainName"],
                            "type": item["Type"],
                            # "line": self.record_line(key=item["Line"]),
                            "value": item["Value"],
                            # "mx": item["Priority"] if "Priority" in item else "0",
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
                    if item["RR"] != self.prefix_domain and item["Type"] not in ("MX", "TXT", "SRV", "NS") and \
                            item["RR"].endswith(self.prefix_domain):
                        data.append(
                            {
                                "name": item["RR"] + "." + self.second_level_domain,
                                "type": item["Type"],
                                "line": self.record_line(key=item["Line"]),
                                "value": item["Value"],
                                "mx": item["Priority"] if "Priority" in item else "0",
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
                            "mx": item["Priority"] if "Priority" in item else "0",
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

    def add_record(self, rr=None, type=None, line=None, value=None, ttl=600, mx=None):
        """
        添加记录
        :return: True|False
        """
        try:
            if type == "显示URL":
                type = "REDIRECT_URL"

            if type == "隐性URL":
                type = "FORWARD_URL"

            client = AcsClient(self.key, self.secret, 'cn-hangzhou')
            request = AddDomainRecordRequest()
            request.set_accept_format('json')
            request.set_Line(self.record_line(value=line))
            request.set_TTL(600 if int(ttl) < 600 else int(ttl))
            request.set_Value(value)
            request.set_Type(type)
            # request.set_RR(RR + ("." + self.prefix_domain if self.prefix_domain else ""))
            if self.prefix_domain:
                rr = ''.join([rr, ".", self.prefix_domain])
            request.set_RR(rr)
            request.set_DomainName(self.second_level_domain)

            if type == "MX":
                request.set_Priority(mx)

            response = client.do_action_with_exception(request)
            response = json.loads(response)

            if "Code" in response.keys():
                logger.error(F"add record failed: {response}")
                return False

            logger.info(F"add record success: {rr}")
            return True

        except Exception:
            logger.error("add record unknown exception")
            logger.error(traceback.format_exc())
            return False

    def delete_record(self, rr=None):
        """
        删除记录
        :return: True|False
        """
        try:
            client = AcsClient(self.key, self.secret, 'cn-hangzhou')
            request = DeleteSubDomainRecordsRequest()
            request.set_accept_format('json')
            if self.prefix_domain:
                rr = ''.join([rr, ".", self.prefix_domain])
            request.set_RR(rr)
            request.set_DomainName(self.second_level_domain)

            response = client.do_action_with_exception(request)
            # print(str(response, encoding='utf-8'))
            response = json.loads(response)
            totalCount = response["TotalCount"]

            if totalCount == "1":
                logger.info(F"delete record success: {rr}")
                return True

            logger.error(F"delete record failed: {response}")

        except Exception:
            logger.error("delete record unknown exception")
            logger.error(traceback.format_exc())

        return False

    def set_record_status(self, rr=None, status=None):
        """
        修改记录状态
        status {enable|disable}
        :return: True|False
        """
        try:
            if self.get_record_id(rr):
                record_id = self.get_record_id(rr)
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
                logger.info(F"set record status: [{rr} : Disable]")
                return True
            elif response["Status"] == "Enable":
                logger.info(F"set record status: [{rr} : Enable]")
                return True

            logger.error(F"set record status failed: {response}")
            return False

        except Exception:
            logger.error("set record status unknown exception")
            logger.error(traceback.format_exc())
            return False

    def modify_record(self, old_rr=None, new_rr=None, type=None, line=None, value=None,
                      ttl=None, mx=None):
        """
        修改记录
        :return: True|False
        """
        try:
            record_id = self.get_record_id(old_rr)
            if not record_id:
                return False

            if type == "显示URL":
                type = "REDIRECT_URL"

            if type == "隐性URL":
                type = "FORWARD_URL"

            client = AcsClient(self.key, self.secret, 'cn-hangzhou')
            request = UpdateDomainRecordRequest()
            request.set_accept_format('json')
            request.set_RecordId(record_id)
            request.set_RR(new_rr + "." + self.prefix_domain)
            request.set_Type(type)
            request.set_Value(value)
            request.set_Line(self.record_line(value=line))
            request.set_TTL(600 if int(ttl) < 600 else int(ttl))

            if type == "MX":
                request.set_Priority(mx)

            try:
                response = client.do_action_with_exception(request)
                response = json.loads(response)

                if "Code" in response.keys():
                    logger.error(F"modify record failed: {response}")
                    logger.error(response)
                    return False

                logger.info(F"modify record success: [{old_rr} -> {new_rr}]")
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

    rr = "ssss"
    type = "A"
    line = "默认"
    value = "11.1.1.1"
    ttl = 600
    status = "Enable"

    old_rr = "testaaa-fdsafds"
    new_rr = "a2-test"

    aliyun = ALIYUN(domain, account)
    # ret = aliyun.add_record(rr=rr, type="TXT", line=line, value=value, ttl=ttl)
    # print(ret)
    ret = aliyun.delete_record(rr)
    print(ret)
