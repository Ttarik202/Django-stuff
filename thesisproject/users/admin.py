from django.contrib import admin
from .models import CustomUser, CodeUpload, CodeAnalysisResult
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(CodeUpload)
admin.site.register(CodeAnalysisResult)
