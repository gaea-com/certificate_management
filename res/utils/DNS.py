import socket
from dns import resolver


# 获取域名解析出的后端IP列表
# def get_backend_ip(domain: str) -> list:
#     ip_list = []
#     try:
#         addrs = socket.getaddrinfo(domain.strip(), None)
#         for item in addrs:
#             if item[4][0] not in ip_list:
#                 ip_list.append(item[4][0])
#     except Exception as e:
#         print(e)
#     return ip_list


class QueryDNSResolver(object):
    """
    DNS解析查询
    DNS解析，A类、MX、NS、CNAME
    """

    def __init__(self, domain):
        self.domain = domain

    def A_query(self):
        return self.__Base_query('A')

    def MX_query(self):
        return self.__Base_query('MX')

    def NS_query(self):
        """
        NS_items = resolver.query(domain, 'NS')
        for i in NS_items.response.answer:
            for j in i.items:
                print(j.to_next())
        """
        return self.__Base_query('NS')

    def CNAME_query(self):
        """
        CNAME_items = resolver.query(domain, 'CNAME')
        for i in CNAME_items.response.answer:
            for j in i.items:
                print(j.to_next())
        """
        return self.__Base_query('CNAME')

    def __Base_query(self, queryMode):
        try:
            res = resolver.Resolver()
            res.timeout = 30
            res.lifetime = 30
            items = res.query(self.domain, queryMode)
            address_list = []
            for i in items.response.answer:
                for j in i.items:
                    address_list.append(j.to_text())
            return address_list
        except resolver.NoAnswer as e:
            print(F"No Answer: {e}")
        except resolver.NXDOMAIN as e:
            print(F"cannot resolve {self.domain}: Unknown host --> [{e}]")
        except resolver.Timeout as e:
            print(F"Timeout : {self.domain} --> {e}")
        return []

    def ALL_query(self):
        self.__print_info('A')
        print(self.A_query())

        self.__print_info('MX')
        print(self.MX_query())

        self.__print_info('NS')
        print(self.NS_query())

        self.__print_info('CNAME')
        print(self.CNAME_query())

    def __print_info(self, queryMode):
        print('\n====%s====' % str(queryMode))


if __name__ == "__main__":
    # print(get_backend_ip("www.baidu.com"))
    domain = ""
    query_obj = QueryDNSResolver(domain)
    print(query_obj.ALL_query())
    print("\n")
    print(query_obj.A_query())
