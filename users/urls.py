from django.urls import path
from . import views

app_name = "users"
urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
]
