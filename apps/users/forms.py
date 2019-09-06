from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import get_user_model
# from .models import User
from captcha.fields import CaptchaField

User = get_user_model()


class RegisterForm(UserCreationForm):
    """
    用户注册
    """
    # 验证码
    captcha = CaptchaField(error_messages={"invalid": "验证码错误", "required": "请输入验证码"})

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2", "email", "captcha")


# class RegisterForm(forms.ModelForm):
#     username = forms.CharField(
#         required=True,
#         min_length=3,
#         max_length=16,
#         error_messages={
#             "required": "用户名不能为空",
#             "min_length": "用户名最少3位字符",
#             "max_length": "用户名最大16个字符",
#         }
#     )
#     password1 = forms.CharField(
#         required=True,
#         min_length=6,
#         max_length=16,
#         error_messages={
#             "required": "密码不能为空",
#             "min_length": "密码长度最少6位",
#         }
#     )
#     password2 = forms.CharField(
#         required=True,
#         min_length=6,
#         max_length=16,
#         error_messages={
#             "required": "密码不能为空",
#             "min_length": "密码长度最少6位",
#         }
#     )
#
#     class Meta:
#         model = User
#         fields = ("username", "password1", "password2", "email")
#
#         error_messages = {
#             "username": {"required": "用户名不能为空"},
#             "email": {"required": "邮箱不能为空"},
#         }
#
#     def clean(self):
#         cleaned_data = super().clean()
#         username = cleaned_data.get("username")
#         email = cleaned_data.get("email")
#         password1 = cleaned_data.get("password1")
#         password2 = cleaned_data.get("password2")
#
#         if User.objects.filter(username=username).count():
#             raise forms.ValidationError('用户名：{}已存在'.format(username))
#
#         if password1 != password2:
#             raise forms.ValidationError("两次密码输入不一致")
#
#         if User.objects.filter(email=email).count():
#             raise forms.ValidationError('邮箱：{}已存在'.format(email))


class LoginForm(forms.Form):
    """
    用户登陆
    """
    username = forms.CharField(required=True, error_messages={"required": "用户名不能为空"})
    password = forms.CharField(required=True, error_messages={"required": "密码不能为空"})
    # 验证码
    captcha = CaptchaField(error_messages={"invalid": "验证码错误", "required": "请输入验证码"})


class CreateUserForm(UserCreationForm):
    """
    用于管理员创建普通用户
    """

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2", "email")


class PasswordChangeForm(forms.Form):
    """
    修改密码
    """
    password1 = forms.CharField(
        required=True,
        min_length=6,
        max_length=16,
        error_messages={
            "required": u"密码不能为空"
        })

    password2 = forms.CharField(
        required=True,
        min_length=6,
        max_length=16,
        error_messages={
            "required": u"确认密码不能为空"
        })

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("password2")
        if password != confirm_password:
            raise forms.ValidationError("两次密码输入不一致")
