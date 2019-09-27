from django.contrib.auth import get_user_model
from ssl_cert.models import Domain, ToEmail, CustomDomain

User = get_user_model()


def admin_email() -> str:
    queryset = User.objects.filter(username="admin")
    email = queryset.values()[0]["email"]
    return email


def to_email(domain: str) -> list:
    """
    获取admin账号邮箱，及为域名添加了接收邮箱的邮箱
    """
    to = list()
    to.append(admin_email())
    domain_obj = Domain.objects.get(domain=domain)
    queryset = ToEmail.objects.filter(domain=domain_obj).values("email")
    email_list = [item["email"] for item in queryset]
    to.extend(email_list)

    return to


def custom_domain_to_email(domain: str) -> list:
    """
    获取admin账号邮箱，及为域名添加了接收邮箱的邮箱
    """

    to = list()
    to.append(admin_email())
    custom_domain_obj = CustomDomain.objects.get(domain=domain)
    queryset = ToEmail.objects.filter(custom_domain=custom_domain_obj).values("email")
    email_list = [item["email"] for item in queryset]
    to.extend(email_list)
    return to
