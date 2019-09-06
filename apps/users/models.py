from django.db import models
from django.contrib.auth.models import AbstractUser
from ssl_cert.models import Domain

# Create your models here.


class User(AbstractUser):
    # nickname = models.CharField(max_length=255, blank=True, null=True, unique=True)
    email = models.EmailField(unique=True)
    # is_active = models.BooleanField(default=False)
    domain = models.ManyToManyField(Domain, verbose_name="域名", blank=True)

    class Meta(AbstractUser.Meta):
        pass


class ActivateCode(models.Model):
    user = models.ForeignKey(User, verbose_name="用户", on_delete=models.CASCADE)
    code = models.CharField(verbose_name="激活码", max_length=255)
    expire_time = models.DateTimeField(verbose_name="过期时间")
    create_time = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    update_time = models.DateTimeField(verbose_name="更新时间", auto_now=True)

    class Meta:
        ordering = ("-id",)
        verbose_name = "激活码"
        verbose_name_plural = verbose_name
