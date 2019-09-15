import os
import logging
import time
import shutil
import re
from threading import Thread
from urllib3.contrib import pyopenssl as reqs
import OpenSSL
from datetime import datetime, timedelta
from django.shortcuts import render
from django.views.generic.base import View, TemplateView
from django.views.generic import ListView
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from .models import Domain, SSLCertContent, SubDomains, SubSyncLimit, ToEmail
from .config import dns_api_mode, CERT_DIR
from res.ssl_cert import SSLCert
from apps.mixin import LoginRequiredMixin
from res.acme import Acme
from res.domain import DomainClassify
from res.email_table.send_ssl_cert_email_table import email_table
from res.custom_send_email import send_email

# Create your views here.

log = logging.getLogger('django')

User = get_user_model()


class IndexView(LoginRequiredMixin, TemplateView):
    """
    首页
    """
    template_name = "ssl_cert/index.html"


@login_required
def domain_list(request):
    """
    域名列表
    """
    page = request.GET.get('page')
    limit = request.GET.get('limit', 20)
    search_content = request.GET.get('searchContent', "")
    # 如果是管理员账号，返回全部域名，如果是普通账号，返回授权的域名
    # TODO 此功能未启用
    # user_obj = get_object_or_404(User, username=request.user)
    # if user_obj.is_superuser:
    #     query = Domain.objects.filter(Q(domain__contains=search_content) | Q(dns__contains=search_content)).order_by(
    #         '-id')
    # else:
    #     query = user_obj.domain.filter(Q(domain__contains=search_content) | Q(dns__contains=search_content)).order_by(
    #         '-id')
    query = Domain.objects.filter(Q(domain__contains=search_content) | Q(dns__contains=search_content)).order_by(
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

    data = {
        "code": 0,
        "msg": "",
        "count": count,
        "data": list(contacts.object_list.values()),
    }

    return JsonResponse(data)


class CreateSSLCertView(LoginRequiredMixin, View):
    """
    创建ssl证书
    """

    def get(self, request):
        dns_list = [item[1] for item in Domain.dns_list]
        return render(request, 'ssl_cert/create_ssl_cert.html', {"dns_list": dns_list})

    def post(self, request):
        domain = request.POST.get("domain")
        extensive_domain = True if request.POST.get("extensiveDomainOpen") == "on" else False
        dns = request.POST.get("selectDns")
        comment = request.POST.get("comment")
        dns_account = {}
        for i, k in enumerate(dns_api_mode[dns]):
            dns_account[k] = request.POST.get("dnsAccount" + str(i + 1))

        if Domain.objects.filter(domain=domain).exists():
            return JsonResponse({"status": "failed", "message": "域名已存在", "form": request.POST})

        Domain(
            domain=domain,
            extensive_domain=extensive_domain,
            status="pending",
            dns=dns,
            dns_account=dns_account,
            comment=comment,
        ).save()

        # 创建证书
        ssl_cert = SSLCert(domain, extensive_domain, dns, dns_account)
        t = Thread(target=ssl_cert.create)
        t.daemon = True
        t.start()

        return JsonResponse({"status": "success"})


class BatchCreateSslCertView(LoginRequiredMixin, View):
    """
    批量创建ssl证书: 校验部分
    """

    def post(self, request):
        multiple_domain = request.POST.get('batchCreateSSL').split("\n")
        if len(multiple_domain) > 50:
            log.error("batch create ssl: content too long")
            return JsonResponse({"status": "max_limit", "message": "content too long"})
        new_multiple_domain = []
        log.info(F"batch create ssl cert: {multiple_domain}")
        for line in multiple_domain:
            if not line: continue
            line = line.strip()
            if len(line.split(',')) < 5 or len(line.split(',')) >= 7 or line.split(',')[4] not in ("on", "off"):
                log.error(F"Format incorrect: {line}")
                return JsonResponse({"status": "incorrect", "message": line})
            if Domain.objects.filter(domain=line.split(',')[0].strip()).exists():
                log.error(F"domain exist: {line.split(',')[0]}")
                return JsonResponse({"status": "exist", "message": line.split(',')[0]})
            if not dns_api_mode.get(line.split(',')[1].strip().lower()):
                log.error(F"dns not exist: {line.split(',')[0]} {line.split(',')[1]}")
                return JsonResponse({"status": "not exist", "message": line.split(',')[1]})

            new_multiple_domain.append(line.split(','))

        t = Thread(target=exec_batch_create, args=(new_multiple_domain,))
        t.daemon = True
        t.start()
        return JsonResponse({"status": "success"})


# @login_required
def exec_batch_create(domain_list: list):
    """
    批量创建ssl证书: 执行创建部分
    """
    # thread_list = []
    for item in domain_list:
        print(item)
        dns_account = {}
        for i, k in enumerate(dns_api_mode[item[1]]):
            dns_account[k] = item[i + 2].strip()
        extensive_domain = True if item[4] == "on" else False

        # 保存域名
        Domain(
            domain=item[0].strip(),
            extensive_domain=extensive_domain,
            status="pending",
            dns=item[1].strip().lower(),
            dns_account=dns_account,
            comment=item[-1] if len(item) == 6 else "",
        ).save()

        # 创建证书
        ssl_cert = SSLCert(item[0], extensive_domain, item[1].lower(), dns_account)
        t = Thread(target=ssl_cert.create)
        t.start()
        t.join()
        # thread_list.append(t)
        time.sleep(2)

    # for t in thread_list:
    #     t.join()


def parse_ssl_cert(cert_content):
    """
    解析上传的证书
    """
    try:
        x509 = reqs.OpenSSL.crypto.load_certificate(reqs.OpenSSL.crypto.FILETYPE_PEM, cert_content)
        start_date = datetime.strptime(x509.get_notBefore().decode()[0:-1], '%Y%m%d%H%M%S')
        expire_date = datetime.strptime(x509.get_notAfter().decode()[0:-1], '%Y%m%d%H%M%S')
        domain_list = reqs.get_subj_alt_name(x509)

        domain = None
        extensive_domain = False
        domain_list = [i[1] for i in domain_list]
        for d in domain_list:
            if "*" in d:
                extensive_domain = True
                domain = ''.join(d.split('*.'))
            else:
                domain = d

        return domain, extensive_domain, start_date, expire_date
    except OpenSSL.crypto.Error:
        return None, False, False, False


def save_cert_to_file(domain, cert_content, key_content):
    """
    将上传的证书保存在本地文件中
    """
    if not os.path.isdir(os.path.join(CERT_DIR, domain)):
        os.mkdir(os.path.join(CERT_DIR, domain))

    cert_file = os.path.join(CERT_DIR, domain, "fullchain.cer")
    key_file = os.path.join(CERT_DIR, domain, "{}.key".format(domain))

    with open(cert_file, 'w') as cf, open(key_file, 'w') as kf:
        cf.write(cert_content + "\n")
        kf.write(key_content + "\n")
        log.info(F"The contents of the certificate are saved in the file: {domain}")


def save_cert_to_db(domain, extensive_domain, start_date, expire_date, dns, dns_account, comment, cert_content,
                    key_content):
    """
    将上传的证书保存在数据库中
    """
    domain_obj = Domain.objects.create(
        domain=domain,
        extensive_domain=extensive_domain,
        status="valid",
        start_date=start_date,
        expire_date=expire_date,
        dns=dns,
        dns_account=dns_account,
        comment=comment,
    )

    SSLCertContent.objects.create(
        cert_content=cert_content,
        key_content=key_content,
        domain=domain_obj
    )

    log.info(F"The certificate content has been saved in the database: {domain}")


from res.dns_api.aliyun import ALIYUN
from res.dns_api.cloudflare import CLOUDFLARE
from res.dns_api.dnspod import DNSPOD
import random
import string


def verify_account(dns, domain, account):
    """
    验证上传证书时提交的账号是否可以使用
    验证方式:
        添加txt记录类型
        获取记录列表
        匹配添加的txt记录
        删除添加的txt记录
    """
    dns_list = [ALIYUN, CLOUDFLARE, DNSPOD]  # 此变量没有用到
    random_value = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    cls = eval(dns.upper())
    obj = cls(domain, account)
    sub_domain = F"verify_domain_{''.join(random.sample(string.ascii_letters + string.digits, 8))}".lower()
    log.info(F"verify [{domain} - {dns}] account: add record [{sub_domain}]")
    result = obj.add_record(sub_domain, "TXT", "默认", random_value)
    if result:
        time.sleep(1)
        result = obj.delete_record(sub_domain)
        log.info(F"verify [{domain} - {dns}] account: del record [{sub_domain}]")
        return result


class UploadSSLCertView(LoginRequiredMixin, View):
    """
    上传证书
    """

    def get(self, request):
        dns_list = [item[1] for item in Domain.dns_list]
        return render(request, 'ssl_cert/upload_ssl_cert.html', context={"dns_list": dns_list})

    def post(self, request):
        dns = request.POST.get("selectDns")
        dns_account = {}
        for i, k in enumerate(dns_api_mode[dns]):
            dns_account[k] = request.POST.get("dnsAccount" + str(i + 1)).strip()
        cert_content = request.POST.get("cert")
        key_content = request.POST.get("private-key")
        comment = request.POST.get("comment")

        domain, extensive_domain, start_date, expire_date = parse_ssl_cert(cert_content)
        log.info(
            F"parse cert content: [domain: {domain} ext_domain: {extensive_domain} start time: {start_date} end time: {expire_date}]")

        # 解析出来的域名
        if domain:
            # 检查域名是否已存在
            if Domain.objects.filter(domain=domain).exists():
                return JsonResponse({"status": "failed", "msg": "域名已存在"})
            # 验证提交的DNS账号
            if verify_account(dns, domain, dns_account):
                # 将提交的证书内容保存到本地文件中
                save_cert_to_file(domain, cert_content, key_content)
                # # 将提交的证书窝内保存到数据库中
                save_cert_to_db(domain, extensive_domain, start_date, expire_date, dns, dns_account, comment,
                                cert_content, key_content)
                log.info(F"cert upload success: {domain} ")
                return JsonResponse({"status": "success"})
            else:
                log.error(F"DNS API account is incorrect: [{dns} {dns_account}]")
                return JsonResponse({"status": "failed", "msg": "账号验证失败"})
            # return JsonResponse({"status": "success"})
        else:
            log.error("Parse cert file failed, Please check the certificate content")
            return JsonResponse({"status": "failed", "msg": "证书解析失败，请检查证书内容是否有误。"})


class ViewSSLCertView(LoginRequiredMixin, View):
    """
    查看证书文件及key文件
    """

    def get(self, request):
        domain = request.GET.get("domain")
        return render(request, 'ssl_cert/view_ssl_cert.html', {"domain": domain})

    def post(self, request):
        domain = request.POST.get("domain")
        cert_file = os.path.join(CERT_DIR, domain, "fullchain.cer")
        key_file = os.path.join(CERT_DIR, domain, "{}.key".format(domain))
        result = {"cert_content": "无内容", "key_content": "无内容"}
        if os.path.isfile(cert_file):  # 先查找本地是否有证书文件，如果没有，刚从数据库中读取
            with open(cert_file, 'r') as f:
                result["cert_content"] = f.read().strip()
                log.info("cert content read from file")
        else:
            domain_obj = Domain.objects.get(domain=domain)
            result["cert_content"] = SSLCertContent.objects.get(domain=domain_obj).cert_content
            log.info("cert content read from databases")

        if os.path.isfile(key_file):  # 先查找本地是否有证书文件，如果没有，刚从数据库中读取
            with open(key_file, 'r') as f:
                result["key_content"] = f.read().strip()
                log.info("key content read from file")
        else:
            domain_obj = Domain.objects.get(domain=domain)
            result["key_content"] = SSLCertContent.objects.get(domain=domain_obj).key_content
            log.info("key content read from databases")

        return JsonResponse(result)


def file_iterator(file, chunk_size=512):
    """
    指定大小读取文件
    """
    with open(file, 'r') as f:
        while True:
            c = f.read(chunk_size)
            if c:
                yield c
            else:
                break


class DownloadFileView(LoginRequiredMixin, View):
    """
    下载证书文件和key文件
    """

    def get(self, request):
        domain = request.GET.get("domain")
        f_type = request.GET.get("f_type")
        log.info(F"download file: [{domain}]")
        cert_file = os.path.join(CERT_DIR, domain, "fullchain.cer")
        key_file = os.path.join(CERT_DIR, domain, "{}.key".format(domain))
        if f_type == "cert":
            if os.path.isfile(cert_file):
                response = StreamingHttpResponse(file_iterator(cert_file))
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = F'attachment;filename={domain}_fullchain.cer'
                log.info("download ssl cert file from local")
                return response
            else:
                cert_content = Domain.objects.get(domain=domain).ssl_cert_content.cert_content
                response = StreamingHttpResponse(cert_content + "\n")
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = F'attachment;filename={domain}_fullchain.cer'
                log.info("download ssl cert file from databases")
                return response

        elif f_type == "key":
            if os.path.isfile(key_file):
                response = StreamingHttpResponse(file_iterator(key_file))
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = F'attachment;filename={domain}.key'
                log.info("download key file from local")
                return response
            else:
                key_content = Domain.objects.get(domain=domain).ssl_cert_content.key_content
                response = StreamingHttpResponse(key_content + "\n")
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = F'attachment;filename={domain}.key'
                log.info("download key file from databases")
                return response


class UpdateSSLCertView(LoginRequiredMixin, View):
    """
    更新证书
    """

    def post(self, request):
        pk = request.POST.get("id")
        queryset = Domain.objects.filter(id=pk)
        domain = queryset.values()[0]["domain"]
        extensive_domain = queryset.values()[0]["extensive_domain"]
        dns = queryset.values()[0]["dns"]
        dns_account = eval(queryset.values()[0]["dns_account"])
        status = queryset.values()[0]["status"]
        expire_date = queryset.values()[0]["expire_date"]
        now_time = datetime.now()

        if status != "valid":
            return JsonResponse({"status": "failed", "msg": F"域名状态: {queryset[0].get_status_display()}，不能执行更新"})

        if (expire_date - now_time).days >= 30:
            return JsonResponse({"status": "failed", "msg": "请在距离过期日期小于30天时再执行更新"})

        queryset.update(status="pending")

        # 更新证书子线程
        ssl_cert = SSLCert(domain, extensive_domain, dns, dns_account)
        t = Thread(target=ssl_cert.update)
        t.daemon = True
        t.start()

        return JsonResponse({"status": "success"})


class DisableSSLCertView(LoginRequiredMixin, View):
    """
    禁用/启用证书
        只将域名在数据库中的状态设置为无效/有效，并没有执行acme.sh把证书revoke掉
    """

    def post(self, request):
        pk = request.POST.get("id")
        obj = Domain.objects.get(id=pk)
        if obj.status == "valid":
            obj.status = "invalid"
            obj.save()
            log.info(F"{obj.domain} is disabled")
            return JsonResponse({"status": "success", "msg": F"{obj.domain} 已停用"})
        elif obj.status == "invalid":
            obj.status = "valid"
            obj.save()
            log.info(F"{obj.domain} is enabled")
            return JsonResponse({"status": "success", "msg": F"{obj.domain} 已启用"})
        else:
            log.error(F"{obj.domain} 状态 {obj.status}, 不能执行停用")
            return JsonResponse({"status": "failed", "msg": F"域名状态为: {obj.get_status_display()}，不能执行停用"})


class DeleteSSLCertView(LoginRequiredMixin, View):
    """
    删除证书
    """

    def post(self, request):
        pk = request.POST.get("id")
        queryset = Domain.objects.filter(id=pk)
        domain = queryset.values()[0]["domain"]

        # extensive_domain_open = queryset.values()[0]["extensive_domain"]
        # dns = queryset.values()[0]["dns"]
        # account = eval(queryset.values()[0]["dns_account"])

        # 废除证书
        # acme = Acme(domain, dns, account, extensive_domain_open)
        # acme.revoke()
        # acme.remove()

        domain_dir = os.path.join(CERT_DIR, domain)
        if os.path.isdir(domain_dir):
            shutil.rmtree(domain_dir)  # 删除证书目录
            log.info(F"{domain_dir} 目录已删除")

        queryset.delete()  # 删除数据库中的域名记录
        log.info(F"{domain} deleted")
        return JsonResponse({"status": "success"})


class SyncSubDomainView(LoginRequiredMixin, View):
    """
    同步子域名
        先将域名对应的子域名删除
        再将查询的新的子域名写入数据库中

        同步限制频率: 每次同步间隔2分钟
    """

    def post(self, request):
        user = request.user.username
        domain = request.POST.get('domain')
        try:
            SubSyncLimit.objects.get(user=user, domain=domain)  # 查看表中是否存在此用户，不存在则报异常
            if SubSyncLimit.objects.filter(user=user, domain=domain, sync_time__lt=datetime.now()).count() > 0:
                SubSyncLimit.objects.update(user=user, domain=domain, sync_time=(datetime.now() + timedelta(minutes=2)))
            else:
                return JsonResponse({"status": "failed", "msg": "每次同步间隔2分钟"})
        except SubSyncLimit.DoesNotExist:
            SubSyncLimit.objects.create(user=user, domain=domain,
                                        sync_time=(datetime.now() + timedelta(minutes=2))).save()

        domain_queryset = Domain.objects.filter(domain=domain)
        dns = domain_queryset.values()[0]["dns"]
        account = eval(domain_queryset.values()[0]["dns_account"])
        domain_classify = DomainClassify(domain, dns, account)
        https, http = domain_classify.https_http_list()
        if https or http:
            sub_domain_queryset = SubDomains.objects.filter(sub_domain__iendswith=domain)
            sub_domain_queryset.delete()
            for item in https:
                if "verify_https_msg" in item:
                    sub_domain_queryset.create(
                        protocol="https",
                        sub_domain=item["name"],
                        record_type=item["type"],
                        record_value=item["value"],
                        start_date=item["start_date"],
                        expire_date=item["expire_date"],
                        comment=item["verify_https_msg"],
                        domain=domain_queryset[0]
                    )
                else:
                    sub_domain_queryset.create(
                        protocol="https",
                        sub_domain=item["name"],
                        record_type=item["type"],
                        record_value=item["value"],
                        start_date=item["start_date"],
                        expire_date=item["expire_date"],
                        domain=domain_queryset[0]
                    )

            for item in http:
                sub_domain_queryset.create(
                    protocol="http",
                    sub_domain=item["name"],
                    record_type=item["type"],
                    record_value=item["value"],
                    domain=domain_queryset[0]
                )
        return JsonResponse({"status": "success"})


class SubDomainsView(LoginRequiredMixin, ListView):
    """
    获取子域名
    """

    model = SubDomains
    template_name = "ssl_cert/sub_domains.html"
    context_object_name = "sub_domains_list"

    def get_queryset(self):
        """
        当前请求域名的子域名
        """
        domain_obj = get_object_or_404(Domain, domain=self.request.GET.dict()["domain"])
        return super(SubDomainsView, self).get_queryset().filter(domain=domain_obj).order_by("-protocol")

    def get_context_data(self, *, object_list=None, **kwargs):
        """
        在上下文中增加domain变量
        """
        context = super(SubDomainsView, self).get_context_data()
        context["domain"] = self.request.GET.dict()["domain"]
        return context


class DnsView(LoginRequiredMixin, View):
    """
    DNS 解析
    """

    def get(self, request):
        domain = request.GET.get("domain")
        dns = request.GET.get("dns")
        return render(request, 'ssl_cert/dns.html', context={"domain": domain, "dns": dns})

    def post(self, request):
        domain = request.POST.get("domain")
        queryset = Domain.objects.filter(domain=domain)
        dns = queryset.values()[0]["dns"]
        account = eval(queryset.values()[0]["dns_account"])
        cls = eval(dns.upper())
        obj = cls(domain, account)
        record_list = obj.sub_domains()
        return JsonResponse({"record_list": record_list})


class ToEmailView(LoginRequiredMixin, View):
    """
    通知邮箱
    """

    def get(self, request):
        """
        获取邮箱列表
        """
        domain = request.GET.get("domain")
        domain_obj = Domain.objects.get(domain=domain)
        queryset = ToEmail.objects.filter(domain=domain_obj).values("email")
        email_list = [item["email"] for item in queryset]
        return render(request, 'ssl_cert/to_email.html', context={"domain": domain, "email_list": email_list})

    def post(self, request):
        """
        添加邮箱
        """
        domain = request.POST.get("domain")
        email = request.POST.get("email").strip()
        domain_obj = Domain.objects.get(domain=domain)
        if domain_obj.status != "valid":
            return JsonResponse({"status": "failed", "msg": F"域名状态为: {domain_obj.get_status_display()}, 不能执行此操作"})

        if not self.verify_email(email):
            return JsonResponse({"status": "failed", "msg": "请输入合法邮箱"})

        if ToEmail.objects.filter(domain=domain_obj, email=email).exists():
            return JsonResponse({"status": "failed", "msg": "邮箱已存在"})

        ToEmail.objects.create(email=email, domain=domain_obj).save()
        return JsonResponse({"status": "success"})

    def delete(self, request):
        """
        删除邮箱
        """

        d = QueryDict(request.body)
        domain = d.get("domain")
        email = d.get("email")
        domain_obj = Domain.objects.get(domain=domain)
        if domain_obj.status != "valid":
            return JsonResponse({"status": "failed", "msg": F"域名状态为: {domain_obj.get_status_display()}, 不能执行此操作"})
        ToEmail.objects.filter(email=email, domain=domain_obj).delete()
        return JsonResponse({"status": "success"})

    def verify_email(self, email):
        pattern = re.compile('^[\w-]+(\.[\w-]+)*@[\w-]+(\.[\w-]+)+$')
        match_email = pattern.match(email)
        if match_email:
            return True
        return False


class SourceIPView(LoginRequiredMixin, View):
    """
    源站IP
    """

    def get(self, request):
        domain = request.GET.get("domain")
        queryset = Domain.objects.filter(domain=domain)
        source_ip = queryset.values()[0]["source_ip"]
        return render(request, 'ssl_cert/source_ip.html', context={"source_ip": source_ip, "domain": domain})

    def post(self, request):
        """
        添加源站IP
        """
        domain = request.POST.get("domain")
        source_ip = request.POST.get("source_ip")
        domain_obj = Domain.objects.get(domain=domain)
        if domain_obj.status != "valid":
            return JsonResponse({"status": "failed", "msg": F"域名状态为: {domain_obj.get_status_display()}, 不能执行此操作"})

        domain_obj.source_ip = source_ip
        domain_obj.save()

        return JsonResponse({"status": "success"})

    def delete(self, request):
        """
        删除源站IP
        """
        d = QueryDict(request.body)
        domain = d.get("domain")
        domain_obj = Domain.objects.get(domain=domain)
        if domain_obj.status != "valid":
            return JsonResponse({"status": "failed", "msg": F"域名状态为: {domain_obj.get_status_display()}, 不能执行此操作"})
        domain_obj.source_ip = ""
        domain_obj.save()
        return JsonResponse({"status": "success"})


class SendSSLCertView(LoginRequiredMixin, View):
    """
    向邮箱中发送证书
    """

    def post(self, request):
        domain = request.POST.get("domain")
        domain_obj = Domain.objects.get(domain=domain)
        if domain_obj.status != "valid":
            return JsonResponse({"status": "failed", "msg": F"域名状态为: {domain_obj.get_status_display()}, 不能执行此操作"})
        queryset = ToEmail.objects.filter(domain=domain_obj).values("email")
        if not queryset:
            return JsonResponse({"status": "failed", "msg": "请添加接收邮箱"})
        email_list = [item["email"] for item in queryset]

        domain = domain_obj.domain
        dns = domain_obj.dns
        account = eval(domain_obj.dns_account)
        expire_date = domain_obj.expire_date

        domain_classify = DomainClassify(domain, dns, account)
        https_list, http_list = domain_classify.https_http_list()

        content = email_table(domain, dns, expire_date, https_list, http_list)  # 格式化成html table作为邮件内容发送
        subject = F"{domain} SSL证书"
        to_email = email_list
        send_email(subject, content, domain, to_email)

        return JsonResponse({"status": "success"})


class AddRecordView(LoginRequiredMixin, View):
    """
    添加DNS记录
    """

    def get(self, request):
        domain = request.GET.get("domain")
        return render(request, "ssl_cert/add_record.html", context={"domain": domain})

    def post(self, request):
        domain = request.POST.get("domain")
        name = request.POST.get("name")
        record_type = request.POST.get("type")
        line = request.POST.get("line")
        value = request.POST.get("value")
        mx = request.POST.get("mx", None)
        ttl = request.POST.get("ttl", 600)

        queryset = Domain.objects.filter(domain=domain)
        dns = queryset.values()[0]["dns"]
        account = eval(queryset.values()[0]["dns_account"])
        cls = eval(dns.upper())
        obj = cls(domain, account)
        result = obj.add_record(name, record_type, line, value, ttl, mx)
        if result:
            log.info(F"add record success: {name}.{domain}")
            return JsonResponse({"status": "success"})

        log.error(F"add record failed: {name}.{domain}")
        return JsonResponse({"status": "failed"})


class ModifyRecordView(LoginRequiredMixin, View):
    """
    修改DNS记录
    """

    def get(self, request):
        domain = request.GET.get("domain")
        name = request.GET.get("name")
        record_type = request.GET.get("type")
        line = request.GET.get("line")
        value = request.GET.get("value")
        mx = request.GET.get("mx", None)
        ttl = request.GET.get("ttl", 600)

        log.info(F"modify record before:[{request.GET}]")
        return render(request, 'ssl_cert/modify_record.html', context=locals())

    def post(self, request):
        domain = request.POST.get("domain")
        old_name = request.POST.get("old_name")
        new_name = request.POST.get("new_name")
        record_type = request.POST.get("type")
        line = request.POST.get("line")
        value = request.POST.get("value")
        mx = request.POST.get("mx", None)
        ttl = request.POST.get("ttl", 600)

        queryset = Domain.objects.filter(domain=domain)
        dns = queryset.values()[0]["dns"]
        account = eval(queryset.values()[0]["dns_account"])
        cls = eval(dns.upper())
        obj = cls(domain, account)
        result = obj.modify_record(old_name, new_name, record_type, line, value, ttl, mx)
        if result:
            log.info(F"modify record success: [{old_name}.{domain} --> {new_name}.{domain}]")
            log.info(F"modify record after: [{request.POST}]")
            return JsonResponse({"status": "success"})
        else:
            log.error(F"modify record success: [{old_name}.{domain} --> {new_name}.{domain}]")
            log.info(F"modify record after: [{request.POST}]")
            return JsonResponse({"status": "failed"})


class SetRecordStatusView(LoginRequiredMixin, View):
    """
    设置记录状态
    enable|disable
    """

    def post(self, request):
        domain = request.POST.get("domain")
        name = request.POST.get("name")
        status = request.POST.get("status")

        queryset = Domain.objects.filter(domain=domain)
        dns = queryset.values()[0]["dns"]
        account = eval(queryset.values()[0]["dns_account"])
        cls = eval(dns.upper())
        obj = cls(domain, account)
        result = obj.set_record_status(name, status)
        if result:
            log.info(F"set status {status} success: {name}.{domain}")
            return JsonResponse({"status": "success"})
        else:
            log.error(F"set status {status} failed: {name}.{domain}")
            return JsonResponse({"status": "failed"})


class DeleteRecordView(LoginRequiredMixin, View):
    """
    删除记录
    """

    def post(self, request):
        domain = request.POST.get("domain")
        name = request.POST.get("name")

        queryset = Domain.objects.filter(domain=domain)
        dns = queryset.values()[0]["dns"]
        account = eval(queryset.values()[0]["dns_account"])
        cls = eval(dns.upper())
        obj = cls(domain, account)
        result = obj.delete_record(name)
        if result:
            log.info(F"delete record success: [{name}.{domain}]")
            return JsonResponse({"status": "success"})
        else:
            log.error(F"delete record failed: [{name}.{domain}]")
            return JsonResponse({"status": "failed"})


class CheckDomainStatusView(LoginRequiredMixin, View):
    """
    前端页面中检查到创建中状态的域名时，向后端定时发送状态查询，当状态改变时，前端刷新页面
    """

    def get(self, request):
        domain = request.GET.get("domain")
        queryset = Domain.objects.filter(domain=domain)
        status = queryset.values()[0]["status"]
        log.info(F"check domain status: [{domain}: {status}]")
        return JsonResponse({"status": status})
