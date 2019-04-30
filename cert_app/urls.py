from django.urls import path
from . import views

app_name = "cert"
urlpatterns = [
    path('create_cert_page', views.create_cert_page, name="create_cert_page"),
    path('bulk_create_cert_page', views.bulk_create_cert_page, name="bulk_create_cert_page"),
    path('cert_page', views.cert_page, name="cert_page"),
    path('sub_domain_page', views.sub_domain_page, name="sub_domain_page"),
    path('domain_archive', views.domain_archive, name="domain_archive"),

    path("update_ssl_cert/<int:pk>/", views.update_ssl_cert, name="update_ssl_cert"),
    path("disable_ssl_cert/<int:pk>/", views.disable_ssl_cert, name="disable_ssl_cert"),
    path("delete_domain/<int:pk>/", views.delete_domain, name="delete_domain"),
    path("check_domain_status/", views.check_domain_status, name="check_domain_status"),
    path("view_cert/<int:pk>/", views.view_cert, name="view_cert"),
    path('download_cert_file/<str:domain>/', views.download_cert_file, name="download_cert_file"),
    path('download_key_file/<str:domain>/', views.download_key_file, name="download_key_file"),
    path('view_email/<int:pk>/', views.view_email, name="view_email"),
    path('modify_email/', views.modify_email, name="modify_email"),
    path('domain_classify/', views.domain_classify, name="domain_classify"),
    path('dns_info/<str:domain>/', views.dns_info, name="dns_info"),
    path('add_record/', views.add_record, name="add_record"),
    path('modify_record/', views.modify_record, name="modify_record"),
    path('delete_record/', views.delete_record, name="delete_record"),
    path('set_record_status/', views.set_record_status, name="set_record_status"),
    path('upload_cert_page', views.upload_cert_page, name="upload_cert"),

    # path('query_sub_domain/<int:pk>', query_sub_domain, name="query_sub_domain"),

]
