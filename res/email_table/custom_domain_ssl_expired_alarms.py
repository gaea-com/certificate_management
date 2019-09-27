import os
from datetime import datetime, timedelta

"""
自定义域名 SSL证书剩余时间小于等于5天时 邮件通知 table
"""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ssl_email = os.path.join(BASE_DIR, 'templates/ssl_cert/email_template/ssl_email.html')


def custom_domain_alarm_email(domain: str, expire_date: datetime) -> str:
    with open(ssl_email, 'r') as f:
        html = f.read()

    remaining = (expire_date - datetime.now()).days
    expire_date = expire_date.strftime("%Y-%m-%d")
    tbody = F"""
        <thead>
            <tr style="height: 30px">
                <th style="border: 1px solid #ddd;">域名</th>
                <th style="border: 1px solid #ddd;">证书状态</th>
                <th style="border: 1px solid #ddd;">有效期</th>
                <th style="border: 1px solid #ddd;">剩余天数</th>
            </tr>
        </thead>
        <tbody>
            <tr style="height: 30px">
                <td style="border: 1px solid #ddd;">{domain}</td>
                <td style="border: 1px solid #ddd; color: red;">即将过期</td>
                <td style="border: 1px solid #ddd;">{expire_date}</td>
                <th style="border: 1px solid #ddd;">{remaining} 天</th>
            </tr>
        </tbody>
    """
    html = html.replace("{{ ssl_status }}", tbody)
    html = html.replace("{{ sub_domain }}", "")

    return html
