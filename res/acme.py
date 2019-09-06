import subprocess
import traceback
import logging
import os
from apps.ssl_cert.config import acme_alias_mode, ACME_DIR, ACME_STAGING

log = logging.getLogger('django')


def set_env(dns: str, account: dict):
    """
    设置acme调用dns api时 所需环境变量
    :return: dns alias
    """
    # acme规定的dns别名,如: dns_dp
    dns_alias = acme_alias_mode[dns.lower()][0]
    env_key = acme_alias_mode[dns.lower()][1:]
    account_value = list(account.values())

    env_dict = dict(zip(env_key, account_value))

    for k, v in env_dict.items():
        os.environ[k] = v

    return dns_alias


class Acme(object):
    """
    acme 申请证书，更新证书，卸载证书，删除证书
    """

    def __init__(self, domain: str, dns: str, account: dict, extensive_domain_open: bool = True):
        self.acme_dir = ACME_DIR
        self.staging = ACME_STAGING  # --staging 为测试模式
        self.extensive_domain_open = extensive_domain_open  # 是否创建泛域名, 默认创建
        self.domain = domain
        self.dns = dns
        self.account = account

    def cmd_exec(self, cmd):
        """
        执行命令
        :param: cmd str
        :return: True/False
        """
        try:
            log.info("acme exec cmd: {}".format(cmd))
            # 合并stdout和stderr, 通过管道stderr到stdout然后捕获stdout
            child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
            self.stdoutinfo = child.communicate()

            if child.returncode == 0:
                return True
            else:
                return False

        except Exception as e:
            log.error("acme exec failed: {}".format(e))
            log.error(traceback.format_exc())
            return False

    def get_stdout(self):
        """
        获取命令执行后的返回结果
        """
        return self.stdoutinfo[0]

    def create(self):
        """
        创建证书
        """
        dns_alias = set_env(self.dns, self.account)
        if self.staging:
            if self.extensive_domain_open:
                cmd = "{}/acme.sh --issue --dns {} -d {} -d {} --staging".format(self.acme_dir, dns_alias, self.domain,
                                                                                 "*." + self.domain)
            else:
                cmd = "{}/acme.sh --issue --dns {} -d {} --staging".format(self.acme_dir, dns_alias, self.domain)
        else:
            if self.extensive_domain_open:
                cmd = "{}/acme.sh --issue --dns {} -d {} -d {}".format(self.acme_dir, dns_alias, self.domain,
                                                                       "*." + self.domain)
            else:
                cmd = "{}/acme.sh --issue --dns {} -d {}".format(self.acme_dir, dns_alias, self.domain)

        ret = self.cmd_exec(cmd)
        return ret

    def update(self):
        """
        更新证书
        """
        if self.staging:
            if self.extensive_domain_open:
                cmd = "{}/acme.sh --renew -d {} -d {} --staging".format(self.acme_dir, self.domain, "*." + self.domain)
            else:
                cmd = "{}/acme.sh --renew -d {} --staging".format(self.acme_dir, self.domain)
        else:
            if self.extensive_domain_open:
                cmd = "{}/acme.sh --renew -d {} -d {}".format(self.acme_dir, self.domain, "*." + self.domain)
            else:
                cmd = "{}/acme.sh --renew -d {}".format(self.acme_dir, self.domain)

        ret = self.cmd_exec(cmd)
        return ret

    def revoke(self):
        """
        废除证书
        """
        if self.staging:
            if self.extensive_domain_open:
                cmd = "{}/acme.sh --revoke -d {} -d {} --staging".format(self.acme_dir, self.domain, "*." + self.domain)
            else:
                cmd = "{}/acme.sh --revoke -d {} --staging".format(self.acme_dir, self.domain)
        else:
            if self.extensive_domain_open:
                cmd = "{}/acme.sh --revoke -d {} -d {}".format(self.acme_dir, self.domain, "*." + self.domain)
            else:
                cmd = "{}/acme.sh --revoke -d {}".format(self.acme_dir, self.domain)

        ret = self.cmd_exec(cmd)
        return ret

    def remove(self):
        """
        卸载证书
        """
        if self.staging:
            if self.extensive_domain_open:
                cmd = "{}/acme.sh --remove -d {} -d {} --staging".format(self.acme_dir, self.domain, "*." + self.domain)
            else:
                cmd = "{}/acme.sh --remove -d {} --staging".format(self.acme_dir, self.domain)
        else:
            if self.extensive_domain_open:
                cmd = "{}/acme.sh --remove -d {} -d {}".format(self.acme_dir, self.domain, "*." + self.domain)
            else:
                cmd = "{}/acme.sh --remove -d {}".format(self.acme_dir, self.domain)

        ret = self.cmd_exec(cmd)
        return ret
