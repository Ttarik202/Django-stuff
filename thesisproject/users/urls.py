from django.urls import path
from . import views


urlpatterns = [
    path('register', views.users_register),
    path('login', views.users_login),

]
