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
from django.contrib import messages
import re
from django.apps import apps
BASE_DIR = Path(__file__).resolve().parent.parent


genai.configure(api_key=settings.GENAI_API_KEY)


def show_all_models(request):
    model_data = []

    for model in apps.get_models():
        name = model.__name__
        entries = model.objects.all()
        model_data.append((name, entries))

    return render(request, 'users/all_models.html', {'model_data': model_data})


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("users:dashboard")
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

                    prompt = (
                        "You are an expert code reviewer. Carefully analyze the following Python code for code quality, security, readability, maintainability, and best practices. "
                        "List all issues you see clearly. Then give a strict code quality score from 0 to 100 — do NOT be lenient.\n\n"
                        f"{code_content}\n\n"
                        "Important: Put the score at the end on a line by itself in the format: Code Quality Score: X/100"
                    )

                    response = model.generate_content(prompt)
                    ai_feedback = response.text
                    # return here for accidental 999
                    score_match = re.search(
                        r"(?:score|code quality score)[^\d]{0,10}(\b100\b|\b\d{1,2}\b)", ai_feedback, re.IGNORECASE)
                    score = int(score_match.group(1)) if score_match else None

                    # sometimes gemini might return a number above 100.This ensures that only values between 0-100 are accepted
                    if score and not (0 <= score <= 100):
                        score = None

                except Exception as e:
                    ai_feedback = f"Error occurred while generating AI feedback: {str(e)}"

                # Save both outputs
                CodeAnalysisResult.objects.create(
                    upload=upload,
                    output=flake8_output,
                    ai_feedback=ai_feedback,
                    score=score
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
        user=request.user).order_by("-uploaded_at")[:5]
    # to show the score i need to attach related codeanalysis entries.
    for f in uploaded_files:
        try:
            f.analysisresult = CodeAnalysisResult.objects.get(upload=f)
        except CodeAnalysisResult.DoesNotExist:
            f.analysisresult = None
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


@login_required
def reanalyze_file(request, file_id):
    file = get_object_or_404(CodeUpload, id=file_id, user=request.user)
    file_path = file.uploaded_file.path
    ext = os.path.splitext(file.uploaded_file.name)[1].lower()

    if ext != ".py":
        file.status = "Unsupported file type"
        file.save()
        return redirect("users:previous_reviews")

    file.status = "Re-analyzing"
    file.save()

    # Run flake8
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
        flake8_output = f"Error running flake8: {str(e)}"

    # Run Gemini for AI feedback + score
    try:
        with open(file_path, "r") as f:
            code_content = f.read()

        model = genai.GenerativeModel("models/gemini-1.5-pro")

        prompt = (
            "Please review the following Python code and suggest improvements. "
            "At the end, give it a code quality score from 0 to 100 (where 100 is excellent code quality).\n\n"
            f"{code_content}"
        )

        response = model.generate_content(prompt)
        ai_feedback = response.text

        # Extract score from response
        score_match = re.search(
            r"(?:score|code quality score)[^\d]{0,10}(\b100\b|\b\d{1,2}\b)", ai_feedback, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else None

        # sometimes gemini might return a number above 100.This ensures that only values between 0-100 are accepted
        if score and not (0 <= score <= 100):
            score = None

    except Exception as e:
        ai_feedback = f"Error generating AI feedback: {str(e)}"
        score = None

    # Update or create analysis result with score
    CodeAnalysisResult.objects.update_or_create(
        upload=file,
        defaults={
            "output": flake8_output,
            "ai_feedback": ai_feedback,
            "score": score
        }
    )

    file.status = "Re-analysis complete"
    file.save()

    messages.success(request, "Reanalysis complete! ✅")
    return redirect("users:previous_reviews")
