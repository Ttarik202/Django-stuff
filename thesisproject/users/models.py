from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Create your models here.


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True)

    def __str__(self):
        return self.username


# Creates a relationship with the user who uploaded the file. Foreign key makes it so each code upload is connected to the user.Settings line ensures it works with my custom user model. On delete line means that if the user is deleted , users uploads will be deleted as well

# Uploaded file code holds the actual uploaded file and saves it in media/uploaded_code

class CodeUpload(models.Model):
    analysis_result = models.TextField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to="uploaded_code/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_type = models.CharField(max_length=10, blank=True)
    status = models.CharField(max_length=100, default="Pending")

    def __str__(self):
        return f"{self.user.username} - {self.uploaded_file.name}"


class CodeAnalysisResult(models.Model):
    score = models.IntegerField(null=True, blank=True)
    ai_feedback = models.TextField(blank=True, null=True)
    upload = models.OneToOneField(CodeUpload, on_delete=models.CASCADE)
    output = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for {self.upload.uploaded_file.name}"
