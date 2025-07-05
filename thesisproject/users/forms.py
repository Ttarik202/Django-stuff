from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, CodeUpload


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2"]


class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "profile_picture"]
        widgets = {
            "profile_picture": forms.FileInput(attrs={
                "class": "form-control-file",
                "accept": "image/*",
            }),
        }


class CodeUploadForm(forms.ModelForm):
    class Meta:
        model = CodeUpload
        fields = ["uploaded_file"]
