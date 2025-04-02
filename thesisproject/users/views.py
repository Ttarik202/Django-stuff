from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, CodeUploadForm
from django.contrib.auth.decorators import login_required
from .models import CodeUpload
from django.shortcuts import get_object_or_404
# Create your views here.


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {"form": form})


def login_view(request):
    if request.method == "POST":
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("users:dashboard")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def dashboard(request):
    if request.method == "POST":
        form = CodeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.user = request.user
            upload.save()
            return redirect("users:dashboard")
    else:
        form = CodeUploadForm()

    uploaded_files = CodeUpload.objects.filter(
        user=request.user).order_by("-uploaded_at")
    return render(request, "users/dashboard.html", {"form": form, "files": uploaded_files})


@login_required
def profile_view(request):
    if request.method == "POST":
        form = UserProfileForm(
            request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save
            return redirect("users:profile")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "users/profile.html", {"form": form})


@login_required
def delete_file(request, file_id):
    file = get_object_or_404(CodeUpload, id=file_id, user=request.user)
    file.uploaded_file.delete()  # Deletes the uploaded code file from the storage
    file.delete()  # Delets the database entry
    return redirect("users:dashboard")
