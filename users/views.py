from django.shortcuts import render, redirect, render_to_response
from django.template import RequestContext
from .forms import RegisterForm, LoginForm
from django.contrib import auth
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http import JsonResponse
import logging

logger = logging.getLogger("django")


# Create your views here.


def register(request):
    # 从 get 或者 post 请求中获取 next 参数值
    # get 请求中，next 通过 url 传递，即 /?next=value
    # post 请求中，next 通过表单传递，即 <input type="hidden" name="next" value="{{ next }}"/>
    redirect_to = request.POST.get('next', request.GET.get('next', ''))

    if request.method == 'POST':
        # request.POST 是一个类字典数据结构，记录了用户提交的注册信息
        # 这里提交的就是用户名（username）、密码（password）、确认密码、邮箱（email）
        # 用这些数据实例化一个用户注册表单
        form = RegisterForm(request.POST)

        # 验证数据的合法性
        if form.is_valid():
            # 如果提交数据合法，调用表单的 save 方法将用户数据保存到数据库
            form.save()

            if redirect_to:
                return redirect(redirect_to)
            else:
                return redirect('/')
    else:
        # 请求不是 POST，表明用户正在访问注册页面，展示一个空的注册表单给用户
        form = RegisterForm()

    # 渲染模板
    # 如果用户正在访问注册页面，则渲染的是一个空的注册表单
    # 如果用户通过表单提交注册信息，但是数据验证不合法，则渲染的是一个带有错误信息的表单
    # 将记录用户注册前页面的 redirect_to 传给模板，以维持 next 参数在整个注册流程中的传递
    return render(request, 'users/register.html', context={'form': form, 'next': redirect_to})


def login(request):
    redirect_to = request.POST.get('next', request.GET.get('next', '/'))

    if not redirect_to:
        redirect_to = "/"

    hashkey = CaptchaStore.generate_key()
    imgage_url = captcha_image_url(hashkey)

    if request.method == 'POST':
        form = LoginForm(request.POST)

        error_message = "请检查填写的内容"
        if form.is_valid():
            human = True
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = auth.authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return redirect(redirect_to)
                else:
                    # 无效账号
                    error_message = "用户名或密码错误"
                    return render(request, 'registration/login.html', {
                        'form': form,
                        'next': redirect_to,
                        'hashkey': hashkey,
                        'imgage_url': imgage_url,
                        'error_message': error_message,
                    })
            else:
                # 用户名或密码错误
                error_message = "用户名或密码错误"
                return render(request, 'registration/login.html', {
                    'form': form,
                    'next': redirect_to,
                    'hashkey': hashkey,
                    'imgage_url': imgage_url,
                    'error_message': error_message,
                })
        return render(request, 'registration/login.html', {
            'form': form,
            'next': redirect_to,
            'hashkey': hashkey,
            'imgage_url': imgage_url,
            # 'error_message': error_message,
        })

    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {
        'form': form,
        'next': redirect_to,
        'hashkey': hashkey,
        'imgage_url': imgage_url
    })
