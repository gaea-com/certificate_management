import os
import json
import shutil
import logging
import traceback
from threading import Thread, Semaphore
import datetime

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, \
    HttpResponseRedirect, \
    StreamingHttpResponse, \
    JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required  # 登陆认证

from .models import DomainInfo, DnsApiAccounts, SubDomains

from scripts.py.paginator import Paginator
from scripts.py import check_format
from scripts.py.ssl_cert import ssl_cert
from scripts.py.acme import Acme
from .conf import CERT_DIR
from scripts.py.check_format import parameters_verify
from . import conf
from scripts.py.custom_send_email import send_email

# Create your views here.
logger = logging.getLogger('django')


@login_required()
def index(request):
    """
    首页
    """
    domain_list = DomainInfo.objects.all()  # 获取全部数据
    obj_count = len(domain_list)
    limit = 1000
    pagetag_current = request.GET.get('page', 1)
    pagetag_dsp_count = 6
    paginator = Paginator(obj_count, limit, pagetag_current, pagetag_dsp_count)
    messages = domain_list[paginator.obj_slice_start:paginator.obj_slice_end]

    return render(request, 'index.html', {'messages': messages, 'paginator': paginator})


@login_required
def create_cert_page(request):
    """
    创建证书页面
    """
    if request.method == "POST":
        try:
            domain = request.POST.get("domain")
            dns_company = request.POST.get("dns_company")
            to_email = request.POST.get("to_email")
            cc_email = request.POST.get("cc_email").split(",") if request.POST.get("cc_email") else []

            logger.info(request.POST)

            result = parameters_verify(
                domain=domain,
                to_email=to_email,
                cc_email=cc_email,
            )

            if result["status"] == "failed":
                return HttpResponse(json.dumps(result, indent=4))

            domain_obj = DomainInfo(
                domain=domain,
                ext_domain="*." + domain,
                status="pending",
                dns_company=dns_company.lower(),
                user=request.user.username,
                to_email=to_email,
                cc_email=cc_email,
                start_time=datetime.datetime.now(),
                end_time=(datetime.datetime.now() + datetime.timedelta(days=90))
            )
            domain_obj.save()

            account = {}
            account_keys = conf.dns_api_mode[request.POST.get("dns_company").lower()]
            for i, k in enumerate(account_keys):
                account[k] = request.POST.get("api_" + str(i + 1))

            logger.info(F"account: {account}")

            DnsApiAccounts(
                account=account,
                domain_info=domain_obj,
            ).save()

            logger.info("exec create ssl cert...")

            # 开启一个子线程处理域名创建证书
            # logger.info('Parent process %s.' % os.getpid())
            p = Thread(target=ssl_cert, args=(domain,
                                              dns_company.lower(),
                                              account,
                                              to_email,
                                              cc_email,
                                              request.get_host())
                       )
            p.daemon = True
            p.start()
            # logger.info('Child process will start.')

            messages = {
                "status": "success",
                "message": F"证书将在2分钟后发送到您的邮箱中，请注意查收",
            }

            return HttpResponse(json.dumps(messages, indent=4))

        except Exception as e:
            logger.error("添加域名异常: %s" % e)
            logger.error(traceback.format_exc())
            messages = {
                "status": "failed",
                "message": F"添加 {request.POST.get('domain')} 域名异常，请检查",
            }
            return HttpResponse(json.dumps(messages, indent=4))

    # return HttpResponseRedirect(reverse("index"))
    return render(request, 'pages/forms/create_cert.html')


@login_required
def view_cert(request, pk):
    """
    获取证书及key文件内容
    """
    try:

        domain_obj = DomainInfo.objects.filter(id=pk).first()
        domain = domain_obj.domain
        cert_file = os.path.join(CERT_DIR, domain, "fullchain.cer")
        key_file = os.path.join(CERT_DIR, domain, "{}.key".format(domain))

        logger.info("view cert {}: {}".format(pk, domain))

        query_ret = {"cert_content": None, "key_content": None}
        if os.path.isfile(cert_file):
            with open(cert_file, 'r') as f:
                cert_content = f.read().strip()
                query_ret["cert_content"] = cert_content

        if os.path.isfile(key_file):
            with open(key_file, 'r') as f:
                query_ret["key_content"] = f.read().strip()

    except Exception as e:
        query_ret = {"cert_content": None, "key_content": None}
        logger.error("查看证书未知异常，请检查")
        logger.error(traceback.format_exc())

    return HttpResponse(json.dumps(query_ret))


def query_valid_domain():
    """
    查询所有valid状态的域名
    :return: list
    """

    domain_obj = DomainInfo.objects.filter(status="valid").order_by('-pk')
    domains = domain_obj.values("id", "domain")

    return domains


@login_required
def cert_page(request):
    """
    证书页面
    :param request:
    :return: list
    """
    try:
        domains = query_valid_domain()
        logger.info("cert page domains: %s" % domains)

    except Exception:
        domains = []
        logger.error("ssl cert page unknown exception")
        logger.error(traceback.format_exc())

    return render(request, 'pages/cert.html', {"domains": domains})


@login_required
def sub_domain_page(request):
    """
    子域名页面
    :param request:
    :return: list
    """
    if request.method == "GET":
        try:
            logger.info("view sub domain page")
            domains = query_valid_domain()

        except Exception:
            domains = []
            logger.error("view sub domain page unknown exception")
            logger.error(traceback.format_exc())

        return render(request, 'pages/sub_domain.html', {"domains": domains})

    if request.method == "POST":
        try:
            domain_id = request.POST.get("domain_id")
            result = SubDomains.objects.filter(domain_info_id=domain_id).order_by("-protocol").values()

            if result:
                return JsonResponse(list(result), safe=False)

        except Exception:
            logger.error("query part sub domains unknown exception")
            logger.error(traceback.format_exc())

        return JsonResponse(dict())


@login_required
def update_ssl_cert(request, pk):
    """
    更新域名对应证书的有效期
    :param request:
    :param pk: int
    :return: HttpResponse str
    """
    try:
        domain_info = DomainInfo.objects.filter(pk=pk).first()
        # domain = domain_info.values("domain")[0]["domain"]
        domain = domain_info.domain
        dns_company = domain_info.dns_company
        to_email = domain_info.to_email
        cc_email = domain_info.cc_email

        logger.info(json.dumps(
            {
                "Action": "update ssl cert",
                "pk": pk,
                "domain": domain,
                "dnsComany": dns_company,
                "toEmail": to_email,
                "ccEmail": cc_email,
            },
            ensure_ascii=False,
            indent=4))

        api_account_obj = DnsApiAccounts.objects.get(domain_info_id=pk)
        account = api_account_obj.account

        # 开启一个子线程处理域名创建证书
        logger.info('Parent process %s.' % os.getpid())
        p = Thread(target=ssl_cert, args=(domain,
                                          dns_company.lower(),
                                          account,
                                          to_email,
                                          cc_email,
                                          request.get_host()))
        logger.info('Child process will start.')
        p.daemon = True
        p.start()

        DomainInfo.objects.update(start_time=datetime.datetime.now(),
                                  end_time=datetime.datetime.now() + datetime.timedelta(days=90))

        message = {
            "status": "success",
            "message": ""
        }
        return HttpResponse(json.dumps(message, indent=4))

    except ObjectDoesNotExist as e:
        logger.error(F"data record does not exist: {e}")

    except Exception as e:
        logger.error(F"update ssl cert unknown exception")
        logger.error(traceback.format_exc())

    message = {
        "status": "failed",
        "message": "更新证书异常，请检查",
    }
    return HttpResponse(json.dumps(message, indent=4))


@login_required
def disable_ssl_cert(request, pk):
    """
    停用证书 或 启用证书
    :param request:
    :param pk: int
    :return: HttpResponse str
    """
    try:
        domain_info = DomainInfo.objects.filter(pk=pk)
        domain_status = domain_info.values("status")[0]["status"]
        domain = domain_info.values("domain")[0]["domain"]

        if domain_status == "valid":
            domain_info.update(status="invalid")

            logger.info("{} is disabled".format(domain))

            return HttpResponse("invalid")

        elif domain_status == "invalid":
            domain_info.update(status="valid")

            logger.info("{} is enabled".format(domain))

            return HttpResponse("valid")

        return HttpResponse("{} 状态无相关操作".format(domain_status))

    except Exception as e:
        logger.error(F"Disable|Enable ssl cert unknown exception")
        logger.error(traceback.format_exc())
        return HttpResponse("Disable|Enable ssl cert unknown exception")


@login_required
def delete_domain(request, pk):
    """
    移除证书，删除数据库中的记录，删除证书所在目录
    普通域名 及 泛域名都会一并删除
    :return:
    """
    try:
        domain_info = DomainInfo.objects.filter(pk=pk)
        domain = domain_info.values("domain")[0]["domain"]

        logger.info(F"delete ssl cert: {domain}")

        acme = Acme()
        acme.revoke_cert(domain)
        acme.remove_cert(domain)

        domain_dir = os.path.join(CERT_DIR, domain)

        # 删除域名目录
        try:
            if os.path.isdir(domain_dir):
                shutil.rmtree(domain_dir)
                logger.info("ssl cert dir : {}".format(domain_dir))

        except FileNotFoundError as e:
            logger.error(e)
        except NotADirectoryError as e:
            logger.error(e)

        # 删除数据库中记录
        domain_info.delete()
        logger.info(F"ssl cert was deleted: {domain}")

        return HttpResponse("delete_success")

    except IndexError as e:
        logger.error(F"This record has been deleted, id: {pk}")
        logger.error(e)
        return HttpResponse("delete_success")

    except Exception as e:
        logger.error(F"Error, delete domain unknown exception, id: {pk}")
        logger.error(e)
        logger.error(traceback.format_exc())

        return HttpResponse("Error, 删除域名发生未知异常, id: {}".format(pk))


@login_required
def download_cert_file(request, domain):
    try:
        cert_file = os.path.join(CERT_DIR, domain, "fullchain.cer")

        if not os.path.isfile(cert_file):
            domain_obj = DomainInfo.objects.filter(status="valid")
            domains = domain_obj.values("domain")
            logger.error(F"not found ssl cert file: {domain}")
            return render(request, 'pages/cert.html', {'domains': domains})

        def file_iterator(cert_file, chunk_size=512):
            with open(cert_file, 'r') as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        the_file_name = cert_file
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = F'attachment;filename={domain}_fullchain.cer'

        logger.info("download ssl cert file: %s" % response)
        return response

    except Exception as e:
        logger.error("download ssl cert file unknown exception")
        logger.error(traceback.format_exc())
        return render(request, 'pages/cert.html')


@login_required
def download_key_file(request, domain):
    try:
        key_file = os.path.join(CERT_DIR, domain, "{}.key".format(domain))

        if not os.path.isfile(key_file):
            domain_obj = DomainInfo.objects.filter(status="valid")
            domains = domain_obj.values("domain")
            logger.error(F"not found key file: {domain}")
            return render(request, 'pages/cert.html', {'domains': domains})

        def file_iterator(key_file, chunk_size=512):
            with open(key_file, 'r') as f:
                while True:
                    c = f.read(chunk_size)
                    if c:
                        yield c
                    else:
                        break

        the_file_name = key_file
        response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = F'attachment;filename={domain}.key'

        logger.info("download key file: %s" % response)
        return response

    except Exception:
        logger.error("download key file unknown exception")
        logger.error(traceback.format_exc())
        return render(request, 'pages/cert.html')


@login_required
def check_domain_status(request):
    """
    前端定时器接口
    查询前端传过来的某个域名的状态，返回给前端
    :param request:
    :return:
    """

    if request.method == "GET":
        try:
            domain = request.GET.get("domain").strip()

            domain_info = DomainInfo.objects.filter(domain=domain)
            status = domain_info.values("status")[0]["status"]
            id_ = domain_info.values("id")[0]["id"]

            ret = {
                'id': id_,
                'status': status,
            }

            logger.info("check status: {}  {}".format(domain, status))

            return HttpResponse(json.dumps(ret))

        except IndexError as e:
            logger.error(F"from db not found domain, please check: {e}")

            ret = {
                'id': 0,
                'status': "Invalid domain",
            }
            return HttpResponse(json.dumps(ret))

        except Exception:
            logger.error("check domain status unknown exception")
            logger.error(traceback.format_exc())

            ret = {
                'id': 0,
                'status': "exception",
            }
            return HttpResponse(json.dumps(ret))


@login_required
def view_email(request, pk):
    try:
        email_obj = DomainInfo.objects.get(id=pk)
        to_email = email_obj.to_email
        cc_email = email_obj.cc_email

        ret = {
            "to_email": to_email,
            "cc_email": cc_email,
        }

        logger.info("view email: {}".format(ret))

        return HttpResponse(json.dumps(ret))

    except ObjectDoesNotExist as e:
        logger.info(F"No email address was found: {e}")

    except Exception as e:
        logger.error("view email unknown exception")
        logger.error(traceback.format_exc())

    return HttpResponse(json.dumps({
        "to_email": None,
        "cc_email": None,
    }))


@login_required
def modify_email(request):
    try:
        if request.method == "POST":
            pk = request.POST.get("id")
            new_cc_email = request.POST.get("new_cc_email")

            cc_email_list = new_cc_email.split(",")
            logger.info(F"modify email to {cc_email_list}")

            for i in cc_email_list:
                check_ret = check_format.verify_email(i)  # 检查邮箱格式是否正确
                if not check_ret:
                    return HttpResponse("邮箱格式不合法: {}".format(i))

            email_obj = DomainInfo.objects.get(id=pk)
            email_obj.cc_email = new_cc_email
            email_obj.save()

            return HttpResponse("save_success")

    except Exception as e:
        logger.error("modify cc email unknown exception")
        logger.error(traceback.format_exc())

    return HttpResponse("save failed")


@login_required
def bulk_create_cert_page(request):
    if request.method == "POST":
        try:
            data = request.POST.get("bulk_messages")
            data = data.split("\n")

            t = Thread(target=exec_bulk_create, args=(data, request.user.username, request.get_host()), daemon=True)
            t.start()

            return HttpResponse(json.dumps("success"))
        except Exception:
            logger.error(F"bulk create cert unknown exception")
            logger.error(traceback.format_exc())
            return HttpResponse(json.dumps("failed"))

    return render(request, 'pages/forms/bulk_create_cert.html')


def exec_bulk_create(data, user, index_url):
    try:
        if not isinstance(data, list):
            logger.error("The parameter type must be list")

        for i in data:
            if len(i) == 0:
                continue

            i = i.split(',')

            domain = i[0].strip()
            ext_domain = "*." + domain
            dns_company = i[1].strip()
            api_1 = i[2].strip()
            api_2 = i[3].strip()
            to_email = i[4].strip()
            cc_email = i[5:] if len(i) > 5 else []

            logger.info(json.dumps({
                "action": "bulk create ssl cert",
                "domain": domain,
                "dns company": dns_company,
                "to Email": to_email,
                "cc Email": cc_email,
                "user": user,
            }, ensure_ascii=False, indent=4))

            result = parameters_verify(
                domain=domain,
                to_email=to_email,
                cc_email=cc_email,
            )
            if result["status"] == "failed":
                logger.error(result)

                subject = F"{domain} 域名信息校验失败"
                content = F"""
                        域  名: {domain}<br>
                        状  态: 证书创建失败<br><br>
                        报错信息:<br>
                        {result["message"]}<br>
                    """

                send_email(subject, content, domain, to_email, cc_email)

                continue

            domain_obj = DomainInfo(
                domain=domain,
                ext_domain=ext_domain,
                status="pending",
                dns_company=dns_company.lower(),
                user=user,
                to_email=to_email,
                cc_email=cc_email,
                start_time=datetime.datetime.now().strftime("%Y-%m-%d"),
                end_time=(datetime.datetime.now() + datetime.timedelta(days=90)).strftime("%Y-%m-%d")
            )
            domain_obj.save()

            account = {}
            account_keys = conf.dns_api_mode[dns_company.lower()]
            for i, k in enumerate(account_keys):
                account[k] = "api_" + str(i + 1)

            DnsApiAccounts(
                account=account,
                domain_info=domain_obj,
            ).save()

            logger.info(F"bulk create: {domain}")
            ssl_cert(domain, dns_company.lower(), account, to_email, cc_email, index_url)

    except Exception:
        logger.error("exec bulk create unknown exception")


@login_required
def domain_archive(request):
    return render(request, 'pages/domain_archive.html')


@login_required
def domain_classify(request):
    """
    查询一种dns厂商下所有的域名
    :param request:
    :return:
    """
    try:
        if request.method == "GET":
            dns_company = request.GET.get("dns_company")
            domain_obj = DomainInfo.objects.filter(dns_company__iexact=dns_company)
            domain_info = domain_obj.values("domain", "dns_company")

            logger.info(F"domain classify, query dns: {dns_company} all domain")

            print(domain_info)
            return JsonResponse(list(domain_info), safe=False)

    except Exception:
        logger.error("domain classify unknown exception")
        logger.error(traceback.format_exc())

    return JsonResponse(dict())


from scripts.py.dns_api.dnspod import DNSPOD
from scripts.py.dns_api.aliyun import ALIYUN
from scripts.py.dns_api.cloudflare import CLOUDFLARE


@login_required
def dns_info(request, domain):
    d_obj = DomainInfo.objects.filter(domain=domain).first()
    dns_company = d_obj.dns_company
    id_ = d_obj.id

    account_obj = DnsApiAccounts.objects.filter(domain_info_id=id_).first()
    account = account_obj.account

    logger.info(json.dumps({
        "action": "query all sub domains",
        "domain": domain,
        "dns company": dns_company,
    }, ensure_ascii=False, indent=4))

    c = eval(dns_company.upper())
    obj = c(domain, account)
    sub_domains = obj.sub_domains("part")

    return render(request, 'pages/dns.html',
                  {
                      "top_domain": domain,
                      "dns_company": dns_company,
                      "data": sub_domains
                  })


@login_required
def add_record(request):
    try:
        if request.method == "POST":
            domain = request.POST.get("top_domain")
            sub_domain = request.POST.get("sub_domain")
            record_type = request.POST.get("record_type")
            line = request.POST.get("line", None)
            record_value = request.POST.get("record_value")
            ttl = request.POST.get("ttl")
            mx = request.POST.get("mx", None)

            obj = DomainInfo.objects.filter(domain=domain).first()
            dns_company = obj.dns_company
            id_ = obj.id

            account_obj = DnsApiAccounts.objects.filter(domain_info_id=id_).first()
            account = account_obj.account

            logger.info(json.dumps({
                "action": "add record",
                "domain": domain,
                "sub domain": sub_domain,
                "record type": record_type,
                "line": line,
                "record value": record_value,
                "ttl": ttl,
                "mx": mx,
                "dns company": dns_company,
            }, ensure_ascii=False, indent=4))

            c = eval(dns_company.upper())
            obj = c(domain, account)
            result = obj.add_record(sub_domain, record_type, line, record_value, ttl, mx)

            if result:
                logger.info(F"add record success: {domain}")
                return HttpResponse(json.dumps("success"))

            logger.error(F"add record failed: {domain}")
            return HttpResponse(json.dumps("failed"))

    except Exception:
        logger.error("add record unknown exception")
        logger.error(traceback.format_exc())
        return HttpResponse(json.dumps("failed"))


@login_required
def modify_record(request):
    try:
        if request.method == "POST":
            domain = request.POST.get("top_domain")
            dns_company = request.POST.get("dns_company")
            old_sub_domain = request.POST.get("old_sub_domain")
            new_sub_domain = request.POST.get("new_sub_domain")
            record_type = request.POST.get("record_type")
            line = request.POST.get("line", None)
            record_value = request.POST.get("record_value")
            ttl = request.POST.get("ttl")
            mx = request.POST.get("mx", None)

            obj = DomainInfo.objects.filter(domain=domain).first()
            # dns_company = obj.dns_company
            id_ = obj.id

            account_obj = DnsApiAccounts.objects.filter(domain_info_id=id_).first()
            account = account_obj.account

            logger.info(json.dumps({
                "action": "modify record",
                "domain": domain,
                "old sub domain": old_sub_domain,
                "new sub domain": new_sub_domain,
                "record type": record_type,
                "line": line,
                "record value": record_value,
                "ttl": ttl,
                "mx": mx,
                "dns company": dns_company,
            }, ensure_ascii=False, indent=4))

            c = eval(dns_company.upper())
            obj = c(domain, account)
            result = obj.modify_record(old_sub_domain, new_sub_domain, record_type, line, record_value, ttl, mx)

            if result:
                logger.info(F"modify record success: [{old_sub_domain} -> {new_sub_domain}]")
                return HttpResponse(json.dumps("success"))

            logger.error(F"modify record failed: {old_sub_domain}")
            return HttpResponse(json.dumps("failed"))

    except Exception:
        logger.error("modify record unknown exception")
        logger.error(traceback.format_exc())
        return HttpResponse(json.dumps("failed"))


@login_required
def delete_record(request):
    try:
        if request.method == "POST":
            domain = request.POST.get("top_domain")
            dns_company = request.POST.get("dns_company")
            sub_domain = request.POST.get("sub_domain")

            query_obj = DomainInfo.objects.filter(domain=domain).first()
            id_ = query_obj.id

            account_obj = DnsApiAccounts.objects.filter(domain_info_id=id_).first()
            account = account_obj.account

            logger.info(json.dumps({
                "action": "delete record",
                "domain": domain,
                "sub domain": sub_domain,
                "dns company": dns_company,
            }, ensure_ascii=False, indent=4))

            c = eval(dns_company.upper())
            obj = c(domain, account)
            result = obj.delete_record(sub_domain)

            if result:
                logger.info(F"delete record success: {domain}")
                return HttpResponse(json.dumps("success"))

            logger.error(F"delete record failed: {domain}")
            return HttpResponse(json.dumps("failed"))

    except Exception:
        logger.error("delete record unknown exception")
        logger.error(traceback.format_exc())
        return HttpResponse(json.dumps("failed"))


@login_required
def set_record_status(request):
    try:
        if request.method == "POST":
            domain = request.POST.get("top_domain")
            dns_company = request.POST.get("dns_company")
            sub_domain = request.POST.get("sub_domain")
            status = request.POST.get("status")

            query_obj = DomainInfo.objects.filter(domain=domain).first()
            id_ = query_obj.id

            account_obj = DnsApiAccounts.objects.filter(domain_info_id=id_).first()
            account = account_obj.account

            logger.info(json.dumps({
                "action": "set record status",
                "domain": domain,
                "sub domain": sub_domain,
                "dns company": dns_company,
                "status": status,
            }, ensure_ascii=False, indent=4))

            c = eval(dns_company.upper())
            obj = c(domain, account)
            result = obj.set_record_status(sub_domain, status)

            if result:
                logger.info(F"set record status success: [{sub_domain} : {status}]")
                return HttpResponse(json.dumps("success"))

            logger.info(F"set record status failed: {sub_domain}")
            return HttpResponse(json.dumps("failed"))

    except Exception:
        logger.error("set record status unknown exception")
        logger.error(traceback.format_exc())
        return HttpResponse(json.dumps("failed"))


import OpenSSL


def parse_ssl_cert(cert_pem):
    try:
        from urllib3.contrib import pyopenssl as reqs
        x509 = reqs.OpenSSL.crypto.load_certificate(reqs.OpenSSL.crypto.FILETYPE_PEM, cert_pem)
        start_time = datetime.datetime.strptime(x509.get_notBefore().decode()[0:-1], '%Y%m%d%H%M%S')
        end_time = datetime.datetime.strptime(x509.get_notAfter().decode()[0:-1], '%Y%m%d%H%M%S')
        domain_list = reqs.get_subj_alt_name(x509)

        domain = None
        for i in domain_list:
            if "*" not in i[1]:
                domain = i[1]

        return domain, start_time, end_time
    except OpenSSL.crypto.Error:
        logger.error(F"Parse certificate failed")
        logger.error(traceback.format_exc())

    except Exception:
        logger.error("parse ssl cert unknown exception")
        logger.error(traceback.format_exc())
    return False, False, False


def save_ssl_cert_content(domain, cert, key):
    logger.info("save ssl cert content")
    os.mkdir(os.path.join(CERT_DIR, domain))

    cert_file = os.path.join(CERT_DIR, domain, "fullchain.cer")
    key_file = os.path.join(CERT_DIR, domain, "{}.key".format(domain))

    with open(cert_file, 'w') as f:
        f.write(cert)

    with open(key_file, 'w') as f:
        f.write(key)


@login_required
def upload_cert_page(request):
    if request.method == "GET":
        return render(request, 'pages/forms/upload_cert.html')

    if request.method == "POST":
        try:
            dns_company = request.POST.get("dns_company")
            to_email = request.POST.get("to_email")
            cc_email = request.POST.get("cc_email").split(",") if request.POST.get("cc_email") else []
            cert_content = request.POST.get("cert_content")
            key_content = request.POST.get("key_content")

            domain, start_time, end_time = parse_ssl_cert(cert_content)
            if not (domain and start_time and end_time):
                logger.error("Not a valid certificate")
                return HttpResponse(json.dumps({
                    "status": "failed",
                    "message": "请检查证书是否符合标准"
                }, indent=4))

            result = parameters_verify(
                domain=domain,
                to_email=to_email,
                cc_email=cc_email,
            )

            if result["status"] == "failed":
                logger.error(result)
                return HttpResponse(json.dumps(result, indent=4))

            account = {}
            account_keys = conf.dns_api_mode[dns_company.lower()]
            for i, k in enumerate(account_keys):
                account[k] = request.POST.get("api_" + str(i + 1))

            logger.info(F"account: {account}")

            domain_obj = DomainInfo(
                domain=domain,
                ext_domain="*." + domain,
                status="valid",
                dns_company=dns_company.lower(),
                user=request.user.username,
                to_email=to_email,
                cc_email=cc_email,
                start_time=start_time,
                end_time=end_time,
            )
            domain_obj.save()

            DnsApiAccounts(
                account=account,
                domain_info=domain_obj,
            ).save()

            save_ssl_cert_content(domain, cert_content, key_content)

            return HttpResponse(json.dumps({
                "status": "success",
                "message": ""
            }, indent=4))

        except Exception:
            logger.error("upload cert unknown exception")
            logger.error(traceback.format_exc())

            return HttpResponse(json.dumps({
                "status": "failed",
                "message": "上传证书未知异常"
            }, indent=4))
