from django.contrib.auth.forms import UserCreationForm
from .models import User
from captcha.fields import CaptchaField
from django import forms


class RegisterForm(UserCreationForm):
    captcha = CaptchaField(error_messages={'invalid': '验证码输入有误'})

    class Meta:
        model = User
        fields = ("username", "email", "captcha")


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '请输入用户名'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "请输入密码"}))
    captcha = CaptchaField(error_messages={"invalid": "验证码错误", "required": "请输入验证码"})

    class Meta:
        model = User
        fields = ("username", "email", "captcha")
