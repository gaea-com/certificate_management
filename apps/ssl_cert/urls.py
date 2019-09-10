from django.urls import path
from . import views

app_name = 'ssl_cert'
urlpatterns = [
    path('domain_list/', views.domain_list, name="domain_list"),
    path('create/', views.CreateSSLCertView.as_view(), name="create"),
    path('batch_create/', views.BatchCreateSslCertView.as_view(), name="batch_create"),
    path('upload_ssl_cert/', views.UploadSSLCertView.as_view(), name="upload_ssl_cert"),
    path('view_ssl_cert/', views.ViewSSLCertView.as_view(), name="view_ssl_cert"),
    path('download_file/', views.DownloadFileView.as_view(), name="download_file"),
    path('update_ssl_cert/', views.UpdateSSLCertView.as_view(), name="update_ssl_cert"),
    path('disable_ssl_cert/', views.DisableSSLCertView.as_view(), name="disable_ssl_cert"),
    path('delete_ssl_cert/', views.DeleteSSLCertView.as_view(), name="delete_ssl_cert"),
    path('sync_sub_domains/', views.SyncSubDomainView.as_view(), name="sync_sub_domains"),
    path('sub_domains/', views.SubDomainsView.as_view(), name="sub_domains"),
    path('dns/', views.DnsView.as_view(), name="dns"),
    path('to_email/', views.ToEmailView.as_view(), name="to_email"),
    path('source_ip/', views.SourceIPView.as_view(), name="source_ip"),
    path('send_ssl_cert_to_email/', views.SendSSLCertView.as_view(), name="send_ssl_cert_to_email"),
    path('add_record/', views.AddRecordView.as_view(), name="add_record"),
    path('modify_record/', views.ModifyRecordView.as_view(), name="modify_record"),
    path('set_record_status/', views.SetRecordStatusView.as_view(), name="set_record_status"),
    path('delete_record/', views.DeleteRecordView.as_view(), name="delete_record"),

    path('check_domain_status/', views.CheckDomainStatusView.as_view(), name="check_domain_status"),
]
