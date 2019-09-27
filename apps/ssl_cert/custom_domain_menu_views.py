import logging
from django.shortcuts import render
from django.views.generic.base import View
from apps.mixin import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.db.models import Q
from django.http import QueryDict
from .models import CustomDomain, ToEmail
from res.domain import VerifyHttps
import re

log = logging.getLogger('django')


class CustomDomainViews(LoginRequiredMixin, View):
    """
    自定义域名菜单接口
    """

    def get(self, request):
        return render(request, 'ssl_cert/custom_domain/custom_domain.html')


@login_required
def custom_domain_list(request):
    """
    自定义域名列表
    """
    page = request.GET.get('page')
    limit = request.GET.get('limit', 20)
    search_content = request.GET.get('searchContent', "")
    query = CustomDomain.objects.filter(
        Q(domain__contains=search_content) | Q(source_ip__contains=search_content)).order_by('-id')
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

    data = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": list(contacts.object_list.values()),
    }

    return JsonResponse(data)


class AddCustomDomainView(LoginRequiredMixin, View):
    """
    添加自定义域名
    """

    def get(self, request):
        return render(request, 'ssl_cert/custom_domain/add_custom_domain.html')

    def post(self, request):
        custom_domain = request.POST.get("custom_domain")
        ip = request.POST.get("ip")
        verify_https = VerifyHttps(custom_domain)
        result = verify_https.get_source_ip_ssl_date(ip)
        log.info(F"add custom domain: {result}")
        if "verify_https_msg" in result:
            return JsonResponse({"status": "failed", "message": result["verify_https_msg"]})
        if not result["status"]:
            return JsonResponse({"status": "failed", "message": "源站没有配置SSL证书"})

        queryset = CustomDomain.objects.filter(domain=custom_domain)
        if queryset.exists():
            return JsonResponse({"status": "failed", "message": "域名已存在"})

        queryset.create(domain=custom_domain, source_ip=ip, start_date=result["start_date"],
                        expire_date=result["expire_date"])
        return JsonResponse({"status": "success"})


class DeleteCustomDomainView(LoginRequiredMixin, View):
    """
    删除自定义域名
    """

    def delete(self, request):
        data = QueryDict(request.body)
        custom_domain = data.get("custom_domain")
        CustomDomain.objects.filter(domain=custom_domain).delete()
        log.info(F"delete custom domain: {custom_domain} success")
        return JsonResponse({"status": "success"})


class CustomDomainToEmailView(LoginRequiredMixin, View):
    """
    通知邮箱
    """

    def get(self, request):
        """
        获取邮箱列表
        """
        domain = request.GET.get("domain")
        domain_obj = CustomDomain.objects.get(domain=domain)
        queryset = ToEmail.objects.filter(custom_domain=domain_obj).values("email")
        email_list = [item["email"] for item in queryset]
        return render(request, 'ssl_cert/custom_domain/to_email.html',
                      context={"domain": domain, "email_list": email_list})

    def post(self, request):
        """
        添加邮箱
        """
        domain = request.POST.get("domain")
        email = request.POST.get("email").strip()
        domain_obj = CustomDomain.objects.get(domain=domain)

        if not self.verify_email(email):
            return JsonResponse({"status": "failed", "msg": "请输入合法邮箱"})

        queryset = ToEmail.objects.filter(custom_domain=domain_obj, email=email)
        if queryset.exists():
            return JsonResponse({"status": "failed", "msg": "邮箱已存在"})

        queryset.create(email=email, custom_domain=domain_obj)
        log.info(F"add to email success: [{domain} -- {email}]")
        return JsonResponse({"status": "success"})

    def delete(self, request):
        """
        删除邮箱
        """

        d = QueryDict(request.body)
        domain = d.get("domain")
        email = d.get("email")
        domain_obj = CustomDomain.objects.get(domain=domain)
        ToEmail.objects.filter(email=email, custom_domain=domain_obj).delete()
        log.info(F"delete to email success: [{domain} -- {email}]")
        return JsonResponse({"status": "success"})

    def verify_email(self, email):
        pattern = re.compile('^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$')
        match_email = pattern.match(email)
        if match_email:
            return True
        return False
