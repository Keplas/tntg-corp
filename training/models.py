from django.db import models
from accounts.models import CustomUser

class TrainingProgram(models.Model):
    CATEGORY_CHOICES = [
        ('farming','Modern & Tech Farming'),
        ('enterprise','Corporate Mid-Market Enterprise'),
        ('financial','Financial Services & Investments'),
    ]
    title = models.CharField(max_length=300)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='training/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    duration_hours = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    certificate_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    is_free = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Enrollment(models.Model):
    STATUS = [('enrolled','Enrolled'),('in_progress','In Progress'),('completed','Completed'),('certificate_requested','Certificate Requested'),('certified','Certified')]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrollments')
    program = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=30, choices=STATUS, default='enrolled')
    progress_percent = models.IntegerField(default=0)
    quiz_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    certificate_paid = models.BooleanField(default=False)
    certificate_issued = models.BooleanField(default=False)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.program.title}"

class TVProgram(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='tv/', blank=True, null=True)
    video_url = models.URLField(blank=True)
    broadcast_schedule = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=100, blank=True)
    is_live = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
