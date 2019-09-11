"""
tieba.baidu.com
    .com 顶级域名/一级域名
    baidu.com 二级域名
    tieba.baidu.com 三级域名
"""


class SLD(object):

    def __init__(self, domain: str):
        self.domain = domain.strip()

    def is_sld(self) -> bool:
        """
        检查域名是否是二级域名
        SLD(second-level domain)
        """
        suffix = self.reg_match()
        if len(self.domain.split(suffix)[0].split(".")) == 1:
            # 说明是二级域名
            return True
        else:
            return False

    def domain_cut(self) -> tuple:
        """
        域名切割
            将一个域名切割为二级域名及其子域名
        """
        if self.is_sld():
            return "", self.domain

        suffix = self.reg_match()
        sld = self.domain.split(suffix)[0].split(".")[-1] + suffix
        sub = self.domain.split("." + sld)[0]
        return sub, sld

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

        return max(suffix_list)


if __name__ == '__main__':
    sld = SLD("baidu.net")
    print(sld.domain_cut())
