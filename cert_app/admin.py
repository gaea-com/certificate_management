from django.contrib import admin
from .models import DomainInfo
from .models import DnsApiAccounts
from .models import CertContent
from .models import SubDomains


# Register your models here.


class DnsApiAccountsAdmin(admin.ModelAdmin):
    list_display = ('account', 'domain_info')

    # 后台显示排序
    ordering = ("-id",)


# 内联显示，在后台DomainAdmin页面可以编辑DnsApiInfoAdmin
class DnsApiAccountsInline(admin.TabularInline):
    model = DnsApiAccounts
    extra = 1  # 不加此参数，在后台DomainAdmin编辑页面，会显示3个编辑DnsApiInfoAdmin domainInfo的空行


class ReceiverEmailAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'to_email', 'cc_email', 'domain_info',
    )

    ordering = ("-id",)


# class ReceiverEmailInline(admin.TabularInline):
#     model = ReceiverEmail
#     extra = 1  # 不加此参数，在后台DomainAdmin编辑页面，会显示3个编辑DnsApiInfoAdmin domainInfo的空行


class DomainInfoAdmin(admin.ModelAdmin):
    # 在后台编辑页面把 DnsApiInfoAdmin 关联进来
    inlines = [DnsApiAccountsInline, ]

    # 后台显示的列
    list_display = (
        'id', 'domain', 'ext_domain', 'status', 'add_time', 'start_time', 'end_time', 'dns_company',
    )

    # 后台显示排序
    ordering = ("-id",)


class CertContentAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'cert_content', 'key_content', 'domain_info',
    )

    ordering = ("-id",)


class SubDomainsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'protocol', 'sub_domain', 'record_type', 'record_value', 'start_time', 'end_time', 'domain_info',
    )

    ordering = ("-id",)


admin.site.register(DomainInfo, DomainInfoAdmin)
admin.site.register(DnsApiAccounts, DnsApiAccountsAdmin)
# admin.site.register(ReceiverEmail, ReceiverEmailAdmin)
admin.site.register(CertContent, CertContentAdmin)
admin.site.register(SubDomains, SubDomainsAdmin)
