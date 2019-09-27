from django.db import models
import datetime

from apps.ssl_cert.config import dns_api_mode


# Create your models here.


class Domain(models.Model):
    """
    域名
    """
    status_list = (
        ("valid", '有效'),
        ("invalid", "无效"),
        ("pending", "创建中"),
        ("failed", "失败"),
    )

    dns_list = [(key.lower(), key) for key in dns_api_mode.keys()]
    """
    dns_list = (
        ("dnspod", "DNSPod"),
        ("cloudflare", "CloudFlare"),
        ("aliyun", "Aliyun"),
    )
    """

    domain = models.CharField(verbose_name='域名', max_length=100, db_index=True, unique=True)
    extensive_domain = models.BooleanField(verbose_name="泛域名")
    status = models.CharField(verbose_name="状态", max_length=20, choices=status_list, default="valid")
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    start_date = models.DateTimeField(verbose_name='开始日期', default=datetime.datetime.now)
    expire_date = models.DateTimeField(verbose_name='过期日期',
                                       default=(datetime.datetime.now() + datetime.timedelta(days=90)))
    dns = models.CharField(verbose_name="DNS解析商", max_length=20, choices=dns_list)
    dns_account = models.CharField(verbose_name="DNS API账号", max_length=150)
    comment = models.TextField(verbose_name="备注", max_length=200, null=True, blank=True)
    source_ip = models.CharField(verbose_name="源站IP", max_length=15, null=True, blank=True)

    class Meta:
        # 数据库中生成的表名称 默认 app名称 + 下划线 + 类名
        # db_table = "domain_info"
        ordering = ("-id",)
        # 定义在管理后台显示的名称
        verbose_name = '域名'
        # 指定复数时的名称(去除复数的s)
        verbose_name_plural = verbose_name

    def __str__(self):
        return F"{self.domain} {self.dns}"

    # 还没用到此方法
    def get_time_diff(self):
        """过期时间减去当前时间得到剩余天数"""
        now = datetime.datetime.now()
        return (self.expire_date - now).days


class ToEmail(models.Model):
    """
    接收证书的邮箱
    """
    email = models.EmailField(verbose_name="邮箱")
    domain = models.ForeignKey("Domain", on_delete=models.CASCADE, blank=True, null=True)
    custom_domain = models.ForeignKey("CustomDomain", on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ("-id",)
        verbose_name = "通知邮箱"
        verbose_name_plural = verbose_name


class SSLCertContent(models.Model):
    """
    域名证书
    """
    cert_content = models.TextField(verbose_name="证书")
    key_content = models.TextField(verbose_name="key")
    domain = models.OneToOneField("Domain", on_delete=models.CASCADE)

    class Meta:
        ordering = ("-id",)
        # 定义在管理后台显示的名称
        verbose_name = '证书内容'
        # 指定复数时的名称(去除复数的s)
        verbose_name_plural = verbose_name

    def __str__(self):
        return F"{self.domain_id}"


class SubDomains(models.Model):
    """
    子域名
    """
    protocol_type = (
        ("http", 'http'),
        ("https", "https"),
    )
    record_type_list = (
        ("A", 'A'),
        ("CNAME", "CNAME"),
        ("AAAA", 'AAAA'),
        ("MX", "MX"),
        ("NS", "NS"),
        ("SRV", 'SRV'),
        ("CAA", "CAA"),
        ("explicit_URL", "explicit_URL"),
        ("implicit_URL", "implicit_URL"),
    )
    protocol = models.CharField(verbose_name="协议", max_length=5, choices=protocol_type)
    sub_domain = models.CharField(verbose_name="子域名", max_length=253, db_index=True)
    record_type = models.CharField(verbose_name="记录类型", max_length=20, choices=record_type_list)
    record_value = models.CharField(verbose_name="记录值", max_length=198)
    start_date = models.DateTimeField(verbose_name="开始日期", blank=True, null=True)
    expire_date = models.DateTimeField(verbose_name="过期日期", blank=True, null=True)
    comment = models.CharField(verbose_name="备注", max_length=50, blank=True, null=True)
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE, verbose_name="主域名")

    class Meta:
        verbose_name = "子域名"
        verbose_name_plural = verbose_name


class SubSyncLimit(models.Model):
    """
    子域名同步频率限制
    每次同步间隔 2 分钟
    """
    user = models.CharField(verbose_name="用户名", max_length=50)
    domain = models.CharField(verbose_name="域名", max_length=100)
    sync_time = models.DateTimeField(verbose_name="同步时间", default=datetime.datetime.now)

    class Meta:
        verbose_name = "子域名同步频率限制"
        verbose_name_plural = verbose_name


class CustomDomain(models.Model):
    """
    自定义域名
    """
    domain = models.CharField(verbose_name="域名", max_length=50)
    source_ip = models.GenericIPAddressField(verbose_name="源站IP")
    start_date = models.DateTimeField(verbose_name='开始日期', blank=True, null=True)
    expire_date = models.DateTimeField(verbose_name='过期日期', blank=True, null=True)

    class Meta:
        verbose_name = "自定义域名"
        verbose_name_plural = verbose_name

    def __str__(self):
        return F"{self.domain} -> {self.source_ip}"
