from django.contrib import admin
from .models import Career, Resume

# Register your models here.
@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = ('role',)
    search_fields = ('role',)

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')