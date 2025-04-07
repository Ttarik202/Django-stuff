from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm, CodeUploadForm
from django.contrib.auth.decorators import login_required
from .models import CodeUpload, CodeAnalysisResult
from django.shortcuts import get_object_or_404
import os
import subprocess
from django.conf import settings
from pathlib import Path
import google.generativeai as genai
BASE_DIR = Path(__file__).resolve().parent.parent


genai.configure(api_key=settings.GENAI_API_KEY)


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
            # get_user() doesnt get the user, it gives the result of the authentication process
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

            filename = upload.uploaded_file.name
            ext = os.path.splitext(filename)[1].lower()
            upload.file_type = ext[1:]

            if ext == ".py":
                upload.status = "Analyzing"
                upload.save()

                file_path = upload.uploaded_file.path

                # Run flake8 analysis
                try:
                    result = subprocess.run(
                        ["flake8", file_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=5
                    )
                    flake8_output = result.stdout or "No issues found ✅"
                except Exception as e:
                    flake8_output = f"Error occurred while running flake8: {str(e)}"

                try:
                    with open(file_path, "r") as f:
                        code_content = f.read()

                    model = genai.GenerativeModel("models/gemini-1.5-pro")

                    prompt = f"Please review the following Python code and suggest improvements:\n\n{code_content}"

                    response = model.generate_content(prompt)
                    ai_feedback = response.text

                except Exception as e:
                    ai_feedback = f"Error occurred while generating AI feedback: {str(e)}"

                # Save both outputs
                CodeAnalysisResult.objects.create(
                    upload=upload,
                    output=flake8_output,
                    ai_feedback=ai_feedback
                )

                upload.status = "Analysis complete"
                upload.save()

            else:
                upload.status = "Unsupported file type"
                upload.save()

            return redirect("users:dashboard")

    else:
        form = CodeUploadForm()

    uploaded_files = CodeUpload.objects.filter(
        user=request.user).order_by("-uploaded_at")
    return render(request, "users/dashboard.html", {
        "form": form,
        "files": uploaded_files
    })


@login_required
def profile_view(request):
    if request.method == "POST":
        form = UserProfileForm(
            request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:profile")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, "users/profile.html", {"form": form})


@login_required
def delete_file(request, file_id):
    file = get_object_or_404(CodeUpload, id=file_id, user=request.user)
    file.uploaded_file.delete()  # Deletes the uploaded code file from the storage
    file.delete()  # Deletes the database entry
    return redirect("users:dashboard")


@login_required
def previous_reviews(request):
    uploads = CodeUpload.objects.filter(
        user=request.user).order_by("-uploaded_at")

    for upload in uploads:
        try:
            upload.analysis = CodeAnalysisResult.objects.get(upload=upload)
        except CodeAnalysisResult.DoesNotExist:
            upload.analysis = None

    return render(request, "users/previous_reviews.html", {"files": uploads})
