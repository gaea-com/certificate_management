from django.urls import path
from . import views

app_name = 'users'
urlpatterns = [
    path('activate/<str:code>/', views.Activate.as_view(), name="activate"),
    path('register/', views.Register.as_view(), name='register'),
    path('login/', views.Login.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),

    path('settings/', views.Setting.as_view(), name="settings"),
    path('user_center/', views.UserCenter.as_view(), name="user_center"),
    path('user_list/', views.UserListView.as_view(), name="user_list"),
    path('is_superuser/', views.IsSuperUser.as_view(), name="is_superuser"),
    path('create_user/', views.CreateUserView.as_view(), name="create_user"),
    path('delete_user/', views.UserDeleteView.as_view(), name="delete_user"),
    path('user_bind_domain/', views.UserBindDomain.as_view(), name="user_bind_domain"),
    path('password_change/', views.PasswordChangeView.as_view(), name="password_change"),
]
