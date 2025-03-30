from django.shortcuts import render

# Create your views here.


def users_register(request):
    return render(request, 'users/users_register.html')


def users_login(request):
    return render(request, 'users/users_login.html')
