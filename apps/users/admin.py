from django.contrib import admin
from .models import User, ActivateCode, EmailConfig


# Register your models here.

# admin.site.register(User)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'password', 'is_staff', 'is_active', 'is_superuser')
    search_fields = ('username', 'email',)


@admin.register(ActivateCode)
class ActivateCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "expire_time", "create_time", "update_time")
    search_fields = ('user',)


@admin.register(EmailConfig)
class EmailConfigAdmin(admin.ModelAdmin):
    list_display = ("email", "password", "server", "port", "ssl")

# admin.site.site_header = "SSL 证书管理后台登录"
# admin.site.site_title = "SSL 证书管理"
