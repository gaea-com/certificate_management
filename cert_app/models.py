from django.db import models
from django.utils import timezone
import datetime
from django_mysql.models import JSONField, ListTextField
import json


# Create your models here.


class DomainInfo(models.Model):
    status_list = (
        ("valid", '有效'),
        ("invalid", "无效"),
        ("pending", "创建中"),
        ("failed", "失败"),
    )

    dns_company_list = (
        ("dnspod", "DNSPod"),
        ("cloudflare", "CloudFlare"),
        ("aliyun", "Aliyun"),
    )

    domain = models.CharField(verbose_name='域名', max_length=255, db_index=True, blank=False, null=False)
    ext_domain = models.CharField(verbose_name="泛域名", max_length=255, blank=True, null=True)
    status = models.CharField(verbose_name="状态", max_length=20, choices=status_list, default="valid", db_index=True)
    add_time = models.DateTimeField(verbose_name="添加时间", auto_now_add=True)
    # start_time = models.DateTimeField(verbose_name='生效时间', default=timezone.now)
    # end_time = models.DateTimeField(verbose_name='过期时间',
    #                                 default=(timezone.now() + datetime.timedelta(days=90)))
    start_time = models.DateTimeField(verbose_name='生效时间', blank=True, null=True)
    end_time = models.DateTimeField(verbose_name='过期时间', blank=True, null=True)
    dns_company = models.CharField(verbose_name="DNS解析商", max_length=20, choices=dns_company_list)
    user = models.CharField(verbose_name="用户名", max_length=50, blank=True, null=True)
    to_email = models.EmailField(verbose_name="接收邮箱", max_length=100)
    cc_email = ListTextField(verbose_name="抄送邮箱", base_field=models.CharField(max_length=100, blank=True, null=True), size=20)

    class Meta:
        # 数据库中生成的表名称 默认 app名称 + 下划线 + 类名
        db_table = "domain_info"
        ordering = ("-id",)
        # 定义在管理后台显示的名称
        verbose_name = '域名'
        # 指定复数时的名称(去除复数的s)
        verbose_name_plural = verbose_name


class DnsApiAccounts(models.Model):
    # key = models.CharField(verbose_name="key", max_length=255)
    # token = models.CharField(verbose_name="token", max_length=255)
    account = JSONField()
    domain_info = models.ForeignKey(DomainInfo, on_delete=models.CASCADE)

    class Meta:
        # 数据库中生成的表名称 默认 app名称 + 下划线 + 类名
        db_table = "dns_api_accounts"
        ordering = ("-id",)
        # 定义在管理后台显示的名称
        verbose_name = 'API账号'
        # 指定复数时的名称(去除复数的s)
        verbose_name_plural = verbose_name

    def __str__(self):
        return json.dumps(self.account)


class CertContent(models.Model):
    cert_content = models.TextField(verbose_name="证书", blank=True, null=True)
    key_content = models.TextField(verbose_name="key", blank=True, null=True)
    domain_info = models.ForeignKey(DomainInfo, on_delete=models.CASCADE)

    class Meta:
        db_table = "cert_content"
        ordering = ("-id",)
        # 定义在管理后台显示的名称
        verbose_name = '证书'
        # 指定复数时的名称(去除复数的s)
        verbose_name_plural = verbose_name


class SubDomains(models.Model):
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

    protocol = models.CharField(verbose_name="协议", max_length=5, choices=protocol_type, blank=True, null=True)
    sub_domain = models.CharField(verbose_name="子域名", max_length=255, blank=True, null=True, db_index=True)
    record_type = models.CharField(verbose_name="记录类型", max_length=20, choices=record_type_list, blank=True, null=True)
    record_value = models.CharField(verbose_name="记录值", max_length=255, blank=True, null=True)
    start_time = models.DateTimeField(verbose_name='生效时间', default=None, blank=True, null=True)
    end_time = models.DateTimeField(verbose_name='过期时间', default=None, blank=True, null=True)
    domain_info = models.ForeignKey(DomainInfo, on_delete=models.CASCADE, verbose_name="主域名")

    class Meta:
        db_table = "sub_domains"
        # 定义在管理后台显示的名称
        verbose_name = '子域名'
        # 指定复数时的名称(去除复数的s)
        verbose_name_plural = verbose_name
