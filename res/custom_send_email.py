# 单独执行py文件时，首先载入django环境
# import os
# import django
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'new_ssl_cert.settings')
# django.setup()
#######
import logging
import os
import shutil
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from apps.ssl_cert.config import CERT_DIR

log = logging.getLogger("django")


def send_email(subject: str, content: str, domain: str, to_email: list):
    subject = subject
    content = content
    sender = settings.DEFAULT_FROM_EMAIL
    to_email.append(settings.EMAIL_HOST_USER)
    receiver = to_email

    msg = EmailMultiAlternatives(subject, content, sender, receiver)
    msg.content_subtype = "html"

    # 证书位置
    ssl_key_file = os.path.join(CERT_DIR, domain, domain + ".key")
    ssl_cert_file = os.path.join(CERT_DIR, domain, "fullchain.cer")

    # 添加附件
    if os.path.isfile(ssl_key_file) and os.path.isfile(ssl_cert_file):
        # 复制一份证书链文件，加上域名作为标识
        new_ssl_cert_file = os.path.join(CERT_DIR, domain, domain + ".fullchain.cer")
        shutil.copy(ssl_cert_file, new_ssl_cert_file)

        msg.attach_file(ssl_key_file)
        msg.attach_file(new_ssl_cert_file)

    msg.send()

    log.info("Email was successfully sent to {}".format(receiver))


if __name__ == "__main__":
    pass
