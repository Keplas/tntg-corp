from django.contrib import admin
from .models import TrainingProgram, Enrollment, TVProgram

admin.site.register(TrainingProgram)
admin.site.register(Enrollment)
admin.site.register(TVProgram)
