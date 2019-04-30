import logging
import os
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from cert_app.conf import CERT_DIR
from certificate_management import settings

logger = logging.getLogger("django")


def send_email(subject=None, content=None, domain=None, to_email=None, cc_email=None):
    subject = subject
    content = content
    sender = settings.DEFAULT_FROM_EMAIL

    receiver = list({to_email, settings.EMAIL_HOST_USER})

    msg = EmailMultiAlternatives(subject, content, sender, receiver, cc=cc_email)
    msg.content_subtype = "html"

    # 证书位置
    ssl_key_file = os.path.join(CERT_DIR, domain, domain + ".key")
    ssl_cert_file = os.path.join(CERT_DIR, domain, "fullchain.cer")

    # 添加附件
    if os.path.isfile(ssl_key_file) and os.path.isfile(ssl_cert_file):
        # 复制一份证书链文件，加上域名作为标识
        import shutil
        new_ssl_cert_file = os.path.join(CERT_DIR, domain, domain + ".fullchain.cer")
        shutil.copy(ssl_cert_file, new_ssl_cert_file)

        msg.attach_file(ssl_key_file)
        msg.attach_file(new_ssl_cert_file)

    msg.send()

    logger.info("Email was successfully sent to {} {}".format(receiver, cc_email))


if __name__ == "__main__":
    pass
