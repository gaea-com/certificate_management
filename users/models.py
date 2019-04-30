from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

# Django 内置的 User 模型， 包含以下一些主要的属性
# username，即用户名
# password，密码
# email，邮箱
# first_name，名
# last_name，姓

class User(AbstractUser):
    nickname = models.CharField(max_length=50, blank=True, null=False)
    email = models.EmailField(unique=True)

    # class Meta(AbstractUser.Meta):
    #     db_table = "user"
