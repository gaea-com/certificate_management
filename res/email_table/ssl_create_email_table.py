import os
from datetime import datetime, timedelta

"""
创建证书，更新证书 邮件通知 table
"""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
html_create_ssl = os.path.join(BASE_DIR, 'templates/ssl_cert/email_template/ssl_email.html')


def email_table(ssl_status: bool, domain: str, dns: str, https_list: list = None, http_list: list = None) -> str:
    with open(html_create_ssl, 'r') as f:
        html = f.read()

    status = "有效" if ssl_status else "无效"
    expire_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d") if ssl_status else ""
    font_color = "color: blue" if ssl_status else "color: red"

    tbody = F"""
        <thead>
            <tr style="height: 30px">
                <th style="border: 1px solid #ddd;">域名</th>
                <th style="border: 1px solid #ddd;">证书状态</th>
                <th style="border: 1px solid #ddd;">有效期</th>
                <th style="border: 1px solid #ddd;">DNS</th>
            </tr>
        </thead>
        <tbody>
            <tr style="height: 30px">
                <td style="border: 1px solid #ddd;">{domain}</td>
                <td style="border: 1px solid #ddd; {font_color};">{status}</td>
                <td style="border: 1px solid #ddd;">{expire_date}</td>
                <td style="border: 1px solid #ddd;">{dns}</td>
            </tr>
        </tbody>
    """
    html = html.replace("{{ ssl_status }}", tbody)

    # 子域名部分
    if https_list or http_list:
        thead_sub_domain = """
                    <thead>
                        <tr style="height: 30px">
                            <th style="border: 0px;" colspan="6">所属子域名</th>
                        </tr>
                        <tr style="height: 30px">
                            <th style="border: 1px solid #ddd;">协议</th>
                            <th style="border: 1px solid #ddd;">主机记录</th>
                            <th style="border: 1px solid #ddd;">记录类型</th>
                            <th style="border: 1px solid #ddd;">记录值</th>
                            <th style="border: 1px solid #ddd;">证书有效期</th>
                            <th style="border: 1px solid #ddd;">剩余天数</th>
                        </tr>
                    </thead>
            """
        t = ""
        now = datetime.now()
        for item in https_list:
            # days = (item["expire_date"] - now).days
            days = "域名与证书不匹配" if "verify_https_msg" in item else str((item["expire_date"] - now).days) + " 天"
            t += F"""
                    <tr style="height: 30px">
                        <td style="border: 1px solid #ddd;">https</td>
                        <td style="border: 1px solid #ddd;">{item['name'].replace("." + domain, "")}</td>
                        <td style="border: 1px solid #ddd;">{item['type']}</td>
                        <td style="border: 1px solid #ddd;">{item["value"]}</td>
                        <td style="border: 1px solid #ddd;">{item["expire_date"].strftime("%Y-%m-%d")}</td>
                        <td style="border: 1px solid #ddd;">{days}</td>
                    </tr>
            """
        for item in http_list:
            t += F"""
                    <tr style="height: 30px">
                        <td style="border: 1px solid #ddd;">http</td>
                        <td style="border: 1px solid #ddd;">{item["name"].replace("." + domain, "")}</td>
                        <td style="border: 1px solid #ddd;">{item["type"]}</td>
                        <td style="border: 1px solid #ddd;">{item["value"]}</td>
                        <td style="border: 1px solid #ddd;"></td>
                        <td style="border: 1px solid #ddd;"></td>
                    </tr>
                """
        tbody_sub_doamin = F"<tbody>{t}</tbody>"
        html = html.replace("{{ sub_domain }}", thead_sub_domain + tbody_sub_doamin)
    else:
        html = html.replace("{{ sub_domain }}", "")

    return html
