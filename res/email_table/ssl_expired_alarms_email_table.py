import os
from datetime import datetime, timedelta

"""
SSL证书剩余时间小于等于5天时 邮件通知 table
"""

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
html_create_ssl = os.path.join(BASE_DIR, 'templates/ssl_cert/email_template/ssl_email.html')


def email_table(main_domain: str, dns: str, main_domain_info: dict, https_sub_domain: list = None) -> str:
    with open(html_create_ssl, 'r') as f:
        html = f.read()
    if "verify_https_msg" in main_domain_info:
        ssl_status = main_domain_info["verify_https_msg"]
    elif main_domain_info["expire"]:
        ssl_status = "即将过期"
    else:
        ssl_status = "有效"
    main_domain_font_color = "color: red" if ssl_status != "有效" else "color: blue"
    remaining = (main_domain_info["expire_date"] - datetime.now()).days
    expire_date = main_domain_info["expire_date"].strftime("%Y-%m-%d")
    tbody = F"""
        <thead>
            <tr style="height: 30px">
                <th style="border: 1px solid #ddd;">域名</th>
                <th style="border: 1px solid #ddd;">证书状态</th>
                <th style="border: 1px solid #ddd;">有效期</th>
                <th style="border: 1px solid #ddd;">剩余天数</th>
                <th style="border: 1px solid #ddd;">DNS</th>
            </tr>
        </thead>
        <tbody>
            <tr style="height: 30px">
                <td style="border: 1px solid #ddd;">{main_domain}</td>
                <td style="border: 1px solid #ddd; {main_domain_font_color};">{ssl_status}</td>
                <td style="border: 1px solid #ddd;">{expire_date}</td>
                <th style="border: 1px solid #ddd;">{remaining} 天</th>
                <td style="border: 1px solid #ddd;">{dns}</td>
            </tr>
        </tbody>
    """
    html = html.replace("{{ ssl_status }}", tbody)

    # 子域名部分
    if https_sub_domain:
        thead_sub_domain = """
                    <thead>
                        <tr style="height: 30px">
                            <th style="border: 0px;" colspan="6">所属子域名</th>
                        </tr>
                        <tr style="height: 30px">
                            <th style="border: 1px solid #ddd;">域名</th>
                            <th style="border: 1px solid #ddd;">证书状态</th>
                            <th style="border: 1px solid #ddd;">有效期</th>
                            <th style="border: 1px solid #ddd;">剩余天数</th>
                        </tr>
                    </thead>
            """
        t = ""
        for item in https_sub_domain:
            days = (item["expire_date"] - datetime.now()).days
            sub_domain_ssl = item["verify_https_msg"] if "verify_https_msg" in item else "即将过期"
            t += F"""
                    <tr style="height: 30px">
                        <td style="border: 1px solid #ddd;">{item['name']}</td>
                        <td style="border: 1px solid #ddd; color: red">{sub_domain_ssl}</td>
                        <td style="border: 1px solid #ddd;">{item["expire_date"].strftime("%Y-%m-%d")}</td>
                        <td style="border: 1px solid #ddd;">{days} 天</td>
                    </tr>
            """
        tbody_sub_doamin = F"<tbody>{t}</tbody>"
        html = html.replace("{{ sub_domain }}", thead_sub_domain + tbody_sub_doamin)
    else:
        html = html.replace("{{ sub_domain }}", "")

    return html
