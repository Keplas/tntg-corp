from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import TrainingProgram, Enrollment, TVProgram

def training_home(request):
    programs = TrainingProgram.objects.filter(is_active=True)
    tv = TVProgram.objects.filter(is_active=True)
    categories = TrainingProgram._meta.get_field('category').choices
    ctx = {'programs': programs, 'tv_programs': tv, 'categories': categories}
    return render(request, 'training/training_home.html', ctx)

def program_detail(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk, is_active=True)
    enrolled = False
    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(user=request.user, program=program).exists()
    return render(request, 'training/program_detail.html', {'program': program, 'enrolled': enrolled})

@login_required
def enroll(request, pk):
    program = get_object_or_404(TrainingProgram, pk=pk, is_active=True)
    _, created = Enrollment.objects.get_or_create(user=request.user, program=program)
    if created:
        messages.success(request, f'Enrolled in "{program.title}" successfully!')
    else:
        messages.info(request, 'You are already enrolled in this program.')
    return redirect('program_detail', pk=pk)

def tv_programs(request):
    tv = TVProgram.objects.filter(is_active=True)
    return render(request, 'training/tv_programs.html', {'tv_programs': tv})
