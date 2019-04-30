import subprocess
import traceback
import logging
import os
import json
from cert_app.conf import acme_alias_mode
from cert_app.conf import ACME_DIR

logger = logging.getLogger('django')


def set_env(dns_company, account):
    """
    设置acme调用dns api时 所需环境变量
    :return: dns alias
    """
    dns_alias = acme_alias_mode[dns_company.lower()][0]

    env_key = acme_alias_mode[dns_company.lower()][1:]
    account_value = list(account.values())

    env_dict = dict(zip(env_key, account_value))

    for k, v in env_dict.items():
        os.environ[k] = v

    logger.info(F"dns alias: {dns_alias}")
    logger.info(F"dns alias: {os.environ}")

    return dns_alias

    # env_key = acme_alias_mode[dns_company.lower()]["env_key"]
    # env_token = acme_alias_mode[dns_company.lower()]["env_token"]
    #
    # dns = acme_alias_mode[dns_company.lower()]["dns_alias"]
    # os.environ[env_key] = api_key
    # os.environ[env_token] = api_token
    #
    # logger.info(json.dumps(
    #     {
    #         "acme dns alias": dns,
    #         "setEnv1": os.environ.get(env_key),
    #         "setEnv2": os.environ.get(env_token),
    #     },
    #     indent=4))

    # return dns


class Acme(object):
    """
    acme 申请证书，更新证书，卸载证书，删除证书
    """

    def __init__(self):
        self.acme_dir = ACME_DIR
        self.staging = False if os.environ.get("STAGING") == "False" else True  # --staging 为测试模式
        self.stdoutinfo = None

    def cmd_exec(self, cmd):
        """
        执行命令
        :param: cmd str
        :return: True/False
        """
        try:
            # 合并stdout和stderr, 通过管道stderr到stdout然后捕获stdout
            child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            self.stdoutinfo = child.communicate()

            logger.info("acme cmd: {}".format(cmd))

            if child.returncode == 0:
                return True
            else:
                return False

        except Exception as e:
            logger.error("命令执行异常，请检查: \n{}".format(e))
            logger.error(traceback.format_exc())
            return False

    def get_cmd_exec_ret(self):
        """
        获取命令执行后的返回结果
        :return str
        """
        return self.stdoutinfo[0]

    def create_cert(self, dns_company, account, domain):
        """
        申请证书
        :param dns_company:
        :param api_account
        :param domain:
        :return: True/False
        """
        ext_domain = "*." + domain
        dns = set_env(dns_company, account)
        if self.staging:
            cmd = "{}/acme.sh --issue --dns {} -d {} -d {} --staging".format(self.acme_dir, dns, domain, ext_domain)
            logger.info("acme.sh 测试模式: \n\tcmd: {}".format(cmd))
        else:
            cmd = "{}/acme.sh --issue --dns {} -d {} -d {}".format(self.acme_dir, dns, domain, ext_domain)
            logger.info("acme.sh 正式模式: \n\tcmd: {}".format(cmd))

        ret = self.cmd_exec(cmd)

        return ret

    def update_cert(self, domain):
        """
        更新证书
        :param domain str
        :return: True/False
        """
        ext_domain = "*." + domain
        if self.staging:
            cmd = "{}/acme.sh --renew -d {} -d {} --staging".format(self.acme_dir, domain, ext_domain)
            ret = self.cmd_exec(cmd)
        else:
            cmd = "{}/acme.sh --renew -d {} -d {}".format(self.acme_dir, domain, ext_domain)
            ret = self.cmd_exec(cmd)

        return ret

    def revoke_cert(self, domain):
        """
        卸载证书
        :param domain str
        :return: True/False
        """
        ext_domain = "*." + domain
        if self.staging:
            cmd = "{}/acme.sh --revoke -d {} -d {} --staging".format(self.acme_dir, domain, ext_domain)
            ret = self.cmd_exec(cmd)
        else:
            cmd = "{}/acme.sh --revoke -d {} -d {}".format(self.acme_dir, domain, ext_domain)
            ret = self.cmd_exec(cmd)

        return ret

    def remove_cert(self, domain):
        """
        :param domain: str
        :return: True/False
        """
        ext_domain = "*." + domain
        if self.staging:
            cmd = "{}/acme.sh --remove -d {} -d {} --staging".format(self.acme_dir, domain, ext_domain)
            ret = self.cmd_exec(cmd)
        else:
            cmd = "{}/acme.sh --remove -d {} -d {}".format(self.acme_dir, domain, ext_domain)
            ret = self.cmd_exec(cmd)

        return ret
