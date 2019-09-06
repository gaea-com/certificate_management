import re
import datetime
import uuid
import json
from threading import Thread
import logging
from django.shortcuts import render, redirect, reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib import auth
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse, HttpResponse
from django.views.generic.base import View, TemplateView
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.contrib.auth import update_session_auth_hash
from django.views.generic.edit import FormView, CreateView
from django.urls import reverse_lazy
from .forms import RegisterForm, PasswordChangeForm, LoginForm, CreateUserForm
from .models import User, ActivateCode
from django.conf import settings
from ssl_cert.models import Domain
from apps.mixin import LoginRequiredMixin
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url

log = logging.getLogger('django')


# Create your views here.


class Activate(View):
    def get(self, request, code):
        query = ActivateCode.objects.filter(code=code, expire_time__gte=datetime.datetime.now())
        if query.count() > 0:
            code_record = query[0]
            code_record.user.is_active = True
            code_record.user.save()
            return render(request, "users/login.html", {"msg": "激活成功,请登陆", "status": "success"})
        else:
            return render(request, "users/login.html", {"msg": "激活失败"})


# def ajax_captcha(request):
#     """
#     验证码输入验证
#     """
#     if request.is_ajax():
#         result = CaptchaStore.objects.filter(response=request.GET.get('response'), hashkey=request.GET.get('hashkey'))
#         if result:
#             data = {'status': 1}
#         else:
#             data = {'status': 0}
#         return JsonResponse(data)


# class Register(View):
#     """
#     用户注册
#     """
#
#     def get(self, request):
#         redirect_to = request.POST.get('next', request.GET.get('next', ''))
#         form = RegisterForm()
#         return render(request, 'users/register.html', context={'form': form, 'next': redirect_to})
#
#     def post(self, request):
#         redirect_to = request.POST.get('next', request.GET.get('next', ''))
#         # 提交的是用户名（username）、密码（password）、邮箱（email）
#         form = RegisterForm(request.POST)
#         # 验证数据的合法性
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.is_active = False
#             user.save()
#
#             activate_code = str(uuid.uuid4()).replace("-", "")
#             expire_time = datetime.datetime.now() + datetime.timedelta(days=2)
#             ActivateCode(user=user, code=activate_code, expire_time=expire_time).save()
#
#             activate_link = "http://%s/users/activate/%s" % (request.get_host(), activate_code)
#             subject = '[SSL证书管理] 账号激活'
#             message = F'注册用户名为: {user.username}, 点击<a href="{activate_link}">请这里</a>激活。<br><br>或复制激活链接至浏览器地址栏中激活账号: {activate_link}'
#             from_email = settings.DEFAULT_FROM_EMAIL
#             recipient_list = [user.email]
#             msg = EmailMultiAlternatives(subject, message, from_email, recipient_list)
#             msg.content_subtype = 'html'
#             Thread(target=msg.send).start()
#             log.info(F"账号: {user.username} 注册成功，已发送激活邮件至: {user.email}")
#
#             return render(request, 'users/login.html',
#                           {"msg": "注册成功，激活邮件已经发送到您的邮箱，请点击邮箱中的激活链接完成激活。"})
#
#         return render(request, 'users/register.html', context={'form': form, 'next': redirect_to})


class Register(CreateView):
    template_name = "users/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        human = True  # 验证码
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        # 发送注册邮件
        self.send_email(user, self.request.get_host())
        msg = "注册成功，激活邮件已经发送到您的邮箱，请前往邮箱完成激活。"
        # return super().form_valid(form)

        context = self.get_context_data()
        context["msg"] = msg
        context["status"] = "success"
        return render(self.request, 'users/login.html', context=context)

    def get_context_data(self, **kwargs):
        # 获取原有的上下文
        context = super().get_context_data(**kwargs)
        # 增加新上下文
        hashkey = CaptchaStore.generate_key()
        image_url = captcha_image_url(hashkey)
        context['hashkey'] = hashkey
        context['image_url'] = image_url

        return context

    def send_email(self, user, host):
        activate_code = str(uuid.uuid4()).replace("-", "")
        expire_time = datetime.datetime.now() + datetime.timedelta(days=2)
        ActivateCode(user=user, code=activate_code, expire_time=expire_time).save()

        activate_link = "http://%s/users/activate/%s" % (host, activate_code)
        subject = '[SSL证书管理] 账号激活'
        message = F'注册用户名为: {user.username}, 点击<a href="{activate_link}">请这里</a>激活。<br><br>或复制激活链接至浏览器地址栏中激活账号: {activate_link}'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        msg = EmailMultiAlternatives(subject, message, from_email, recipient_list)
        msg.content_subtype = 'html'
        Thread(target=msg.send).start()
        log.info(F"账号: {user.username} 注册成功，已发送激活邮件至: {user.email}")


class Login(View):
    """
    登陆
    """

    def get(self, request):
        redirect_to = request.POST.get('next', request.GET.get('next', ''))
        hashkey = CaptchaStore.generate_key()
        image_url = captcha_image_url(hashkey)
        return render(request, 'users/login.html',
                      context={'next': redirect_to, "hashkey": hashkey, "image_url": image_url})

    def post(self, request):
        redirect_to = request.POST.get('next', request.GET.get('next', ''))
        hashkey = CaptchaStore.generate_key()
        image_url = captcha_image_url(hashkey)
        form = LoginForm(request.POST)
        if form.is_valid():
            human = True  # 验证码
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # 检查账号是否存在
            user_exists = User.objects.filter(username=username).first()
            if user_exists is not None:
                # 检查账号的密码是否正确
                user = auth.authenticate(username=username, password=password)
                if user is not None:
                    # 检查账号是否激活
                    if user.is_active:
                        auth.login(request, user)
                        if redirect_to:
                            return redirect(redirect_to)
                        else:
                            return redirect(reverse('index'))
                    else:
                        msg = "账户未激活"
                else:
                    msg = "账号或密码错误"
            else:
                msg = "账号不存在"
            return render(request, 'users/login.html', context={
                'next': redirect_to,
                "msg": msg,
                "username": username,
                "hashkey": hashkey,
                "image_url": image_url
            })
        else:
            pattern = '<li>.*?<ul class=.*?><li>(.*?)</li>'
            errors = str(form.errors)
            form_errors = re.findall(pattern, errors)
            return render(request, 'users/login.html', context={
                'username': request.POST.get('username'),
                "hashkey": hashkey,
                "image_url": image_url,
                "msg": form_errors[0],
            })


class Logout(LoginRequiredMixin, View):
    """退出登陆"""

    def get(self, request):
        auth.logout(request)
        return redirect(reverse('users:login'))


# TODO 功能暂未开发
class Setting(LoginRequiredMixin, TemplateView):
    """
    基础设置
    """
    template_name = "users/settings/general_settings.html"


class UserCenter(LoginRequiredMixin, TemplateView):
    """
    用户中心:
        创建新用户
        删除用户:   单个删除/批量删除
        修改账号类型: 管理员/普通账号
        修改密码
    """
    template_name = "users/settings/user_center.html"


class UserListView(LoginRequiredMixin, View):
    """用户列表"""

    def get(self, request):
        page = request.GET.get('page')
        limit = request.GET.get('limit', 10)
        search_content = request.GET.get('userSearch', "")
        query = User.objects.filter(Q(username__contains=search_content) | Q(email__contains=search_content)).order_by(
            '-id')
        paginator = Paginator(query, limit)
        count = query.count()

        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            # 如果请求的页数不是整数，返回第一页。
            contacts = paginator.page(1)
        except EmptyPage:
            # 如果请求的页数不在合法的页数范围内，返回结果的最后一页。
            contacts = paginator.page(paginator.num_pages)

        fields = ['id', 'username', 'email', 'is_active', 'is_superuser']
        data = {
            "code": 0,
            "msg": "",
            "count": count,
            "data": list(contacts.object_list.values(*fields)),
        }

        return JsonResponse(data)


class IsSuperUser(LoginRequiredMixin, View):
    """
    设置用户为管理员或者普通用户
    """

    def post(self, request):
        pk = request.POST.get('id')
        user_obj = User.objects.get(id=pk)
        if user_obj.is_superuser:
            user_obj.is_superuser = False
        else:
            user_obj.is_superuser = True
        user_obj.save()
        return JsonResponse({"status": "success"})


class CreateUserView(LoginRequiredMixin, View):
    """创建用户"""

    def get(self, request):
        return render(request, 'users/settings/user_create.html')

    def post(self, request):
        log.info(F"create new user: {request.POST}")
        form = CreateUserForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.password = make_password(form.cleaned_data['password1'])
            new_user.save()
            form.save_m2m()
            retsult = {"status": "success"}
        else:
            pattern = '<li>.*?<ul class=.*?><li>(.*?)</li>'
            errors = str(form.errors)
            form_errors = re.findall(pattern, errors)
            retsult = {
                "status": "failed",
                "form_errors": form_errors[0],
            }
        log.info(F"create user status: {retsult}")
        return JsonResponse(retsult, content_type='application/json')


class UserDeleteView(LoginRequiredMixin, View):
    """
    删除用户: 支持单条删除和批量删除
    """

    def post(self, request):
        delete_data = json.loads(request.POST.get("deleteData"))
        pk_list = [item['id'] for item in delete_data]
        User.objects.filter(id__in=pk_list).delete()
        return JsonResponse({"status": "success"})


class UserBindDomain(LoginRequiredMixin, View):
    """
    用户关联域名
    """

    def get(self, request):
        user_obj = get_object_or_404(User, pk=request.GET.get("id"))
        added_domains = user_obj.domain.all()  # 已经绑定到该用户的域名
        all_domains = Domain.objects.all()  # 所有域名
        # 由于前端会从所有域名和已经绑定的域名中过滤出未绑定的域名，所以后端这块不处理，只返回全部域名和已经绑定的域名
        result = dict(user=user_obj, all_domains=all_domains, added_domains=added_domains)
        return render(request, 'users/settings/user_bind_domain.html', result)

    def post(self, request):
        user_obj = get_object_or_404(User, pk=int(request.POST.get("user_id")))
        domain_ids = map(int, request.POST.getlist("domain_ids[]", []))
        user_obj.domain.clear()
        if domain_ids:
            for domain in Domain.objects.filter(pk__in=domain_ids):
                user_obj.domain.add(domain)
        return JsonResponse({"status": True})


class PasswordChangeView(LoginRequiredMixin, View):
    def get(self, request):
        user_obj = get_object_or_404(User, pk=int(request.GET.get("id")))
        return render(request, 'users/settings/password_change.html', {"user": user_obj})

    def post(self, request):
        user_obj = get_object_or_404(User, pk=int(request.POST.get("id")))
        form = PasswordChangeForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["password1"]
            user_obj.set_password(new_password)
            user_obj.save()
            update_session_auth_hash(request, user_obj)
            ret = {"status": "success"}
        else:
            pattern = '<li>.*?<ul class=.*?><li>(.*?)</li>'
            errors = str(form.errors)
            password_change_form_errors = re.findall(pattern, errors)
            ret = {
                'status': 'failed',
                'password_change_form_errors': password_change_form_errors[0]
            }
        return JsonResponse(ret)
