import datetime
# from utils.query_sub_domain import query_subdomains


def table(domain, https_list, http_list):
    """将子域名以html table方式显示"""
    # temp = "<table> \
    #         <thead> \
    #             <tr> \
    #                 <th>协议</th> \
    #                 <th>子域名</th> \
    #             </tr> \
    #         </thead> \
    #         <tbody> \
    #             <tr> \
    #                 <td></td> \
    #                 <td></td> \
    #             </tr> \
    #         </tbody> \
    #     </table>"

    t = """<table style='border-collapse:separate; border-spacing:20px; text-align:center'>
                <thead>
                    <tr>
                        <th>协议</th>
                        <th>子域名</th>
                        <th>记录类型</th>
                        <th>记录值</th>
                        <th>开始时间</th>
                        <th>过期时间</th>
                        <th>剩余天数</th>
                    </tr>
                </thead>
            <tbody>
        """

    if not http_list and not https_list:
        return False
        # t += f"""
        #         <tr>
        #             <td>None</td>
        #             <td>None</td>
        #             <td>None</td>
        #             <td>None</td>
        #             <td>None</td>
        #             <td>None</td>
        #             <td>None</td>
        #         </tr>
        #     """

    for item in https_list:
        now = datetime.datetime.now()
        remaining = (item["end_time"] - now).days

        t += f"""
            <tr>
                <td style='color: green;'>https</td>
                <td>{item["name"] + "." + '.'.join(domain.split('.')[-2:])}</td>
                <td>{item["type"]}</td>
                <td>{item["value"]}</td>
                <td>{item["start_time"].strftime("%Y-%m-%d")}</td>
                <td>{item["end_time"].strftime("%Y-%m-%d")}</td>
                <td>{remaining}</td>
            </tr>
        """

    for item in http_list:
        t += f"""
                <tr>
                    <td>http</td>
                    <td>{item["name"] + "." + '.'.join(domain.split('.')[-2:])}</td>
                    <td>{item["type"]}</td>
                    <td>{item["value"]}</td>
                    <td>None</td>
                    <td>None</td>
                    <td>None</td>
                </tr>
            """

    t += """
            </tbody>
        </table>
    """

    return t
