from django.db import models

# Create your models here.
class Career(models.Model):
    role=models.CharField(max_length=100,unique=True)
    skills=models.JSONField(default=list)
    description=models.TextField(blank=True)

    def __str__(self):
        return self.role


class Resume(models.Model):
    file=models.FileField(upload_to='resumes/')
    uploaded_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name