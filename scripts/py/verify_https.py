import logging
import traceback
import re
import subprocess
from datetime import datetime
from io import StringIO

logger = logging.getLogger('django')


# 查询域名证书到期情况
def verify_https(domain):
    """
    校验域名是否启用了https
    :param domain: str
    :return: data, data
    """
    try:
        f = StringIO()
        comm = f"curl -Ivs https://{domain} --connect-timeout 5"

        result = subprocess.getstatusoutput(comm)
        code = result[0]

        if code == 0:
            f.write(result[1])

            m = re.search('start date: (.*?)\n.*?expire date: (.*?)\n.*?\n', f.getvalue(), re.S)

            start_date = m.group(1)
            expire_date = m.group(2)

            # datetime 字符串转时间数组
            new_start_date = datetime.strptime(start_date, "%b %d %H:%M:%S %Y GMT")
            new_expire_date = datetime.strptime(expire_date, "%b %d %H:%M:%S %Y GMT")

            # 剩余天数
            remaining = (new_expire_date - datetime.now()).days

            logger.info('*' * 30)
            logger.info(f'域名: {domain}')
            logger.info('开始时间: {}'.format(new_start_date))
            logger.info('到期时间: {}'.format(new_expire_date))
            logger.info(f'剩余时间: {remaining}天')
            logger.info('*' * 30)

            # print('*' * 30)
            # print(f'域名: {domain}')
            # print('开始时间: {}'.format(new_start_date))
            # print('到期时间: {}'.format(new_expire_date))
            # print(f'剩余时间: {remaining}天')
            # print('*' * 30)

            return new_start_date, new_expire_date

    except Exception as e:
        logger.info("验证域名是否启动https发生未知错误")
        logger.info(traceback.format_exc())

    return False, False


if __name__ == "__main__":
    verify_https("xjqxz.gaeamobile.net")
