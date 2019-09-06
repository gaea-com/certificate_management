import re


class SLD(object):
    """
    SLD(second-level domain)
    """

    def __init__(self, domain: str):
        self.domain = domain.strip()

    def reg_match(self):
        domain_suffix = [".com", ".cn", ".com.cn", ".gov", ".net", ".edu.cn", ".net.cn", ".org.cn", ".co.jp", ".gov.cn",
                         ".co.uk", ".ac.cn", ".edu", ".tv", ".info", ".ac", ".ag", ".am", ".at", ".be", ".biz", ".bz",
                         ".cc", ".de", ".es", ".eu", ".fm", ".gs", ".hk", ".in", ".info", ".io", ".it", ".jp", ".la",
                         ".md", ".ms", ".name", ".nl", ".nu", ".org", ".pl", ".ru", ".sc", ".se", ".sg", ".sh", ".tc",
                         ".tk", ".tw", ".us", ".co", ".uk", ".vc", ".vg", ".ws", ".il", ".li", ".nz", ".xyz", ".wang",
                         ".shop", ".site", ".club", ".fun", ".online", ".red", ".link", ".ltd", ".mobi", ".vip", ".pro",
                         ".work", ".kim", ".group", ".tech", ".store", ".ren", ".ink", ".pub", ".live", ".wiki",
                         ".design", ".xin", ".top"]

        suffix_list = []
        for suffix in domain_suffix:
            if self.domain.endswith(suffix):
                suffix_list.append(suffix)
        suffix = max(suffix_list)
        if len(self.domain.split(suffix)[0].split(".")) == 1:
            return True
        else:
            return False


if __name__ == '__main__':
    sld = SLD("baidu.com")
    # print(sld.is_sld())
    # print(sld.get_sld())
    print(sld.reg_match())
