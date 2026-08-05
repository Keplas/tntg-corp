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


# ── Training Event / Ticket system ──────────────────────────────────────────
from .models import TrainingEvent, EventTicket

def event_list(request):
    events = TrainingEvent.objects.filter(is_active=True).order_by('event_date')
    return render(request, 'training/event_list.html', {'events': events})

def event_detail(request, pk):
    from django.shortcuts import get_object_or_404
    event   = get_object_or_404(TrainingEvent, pk=pk, is_active=True)
    agenda  = [line.strip() for line in event.agenda.splitlines() if line.strip()]
    already = False
    if request.user.is_authenticated:
        already = EventTicket.objects.filter(event=event, email=request.user.email, status='confirmed').exists()
    return render(request, 'training/event_detail.html', {
        'event': event, 'agenda': agenda, 'already_registered': already
    })

def reserve_spot(request, pk):
    from django.shortcuts import get_object_or_404
    from django.core.mail import send_mail
    from django.conf import settings as djsettings
    from django.template.loader import render_to_string

    event = get_object_or_404(TrainingEvent, pk=pk, is_active=True)

    if event.is_full:
        messages.error(request, 'Sorry — this event is fully booked.')
        return redirect('event_detail', pk=pk)

    if request.method == 'POST':
        spot_type = request.POST.get('spot_type','online')
        name      = request.POST.get('name','').strip()
        email     = request.POST.get('email','').strip()
        spot_type = request.POST.get('spot_type','online')

        if not name or not email:
            messages.error(request, 'Please enter your name and email.')
            return redirect('event_detail', pk=pk)

        # Prevent double booking
        if EventTicket.objects.filter(event=event, email=email, status='confirmed').exists():
            messages.warning(request, 'You already have a confirmed ticket for this event. Check your email.')
            return redirect('my_tickets')

        # Create ticket
        ticket = EventTicket.objects.create(
            event=event,
            user=request.user if request.user.is_authenticated else None,
            name=name,
            email=email,
            spot_type=spot_type,
            status='confirmed',
        )

        # Send confirmation email
        try:
            html_body = render_to_string('training/email_ticket.html', {
                'ticket': ticket,
                'event':  event,
            })
            send_mail(
                subject=f'Your T&TG Training Ticket — {event.title}',
                message=(
                    f'Hi {name},\n\n'
                    f'Your spot is confirmed!\n\n'
                    f'Event: {event.title}\n'
                    f'Ticket: {ticket.ticket_number}\n'
                    f'Date: {event.event_date.strftime("%A, %d %B %Y at %I:%M %p")}\n\n'
                    f'See you there!\nT&TG Trade Corporation\n'
                    f'9 Summerbridge Rd, Toronto, ON M1G 1L8, Canada\n'
                    f'tom.grouptrade@gmail.com | +1 (416) 832 3512'
                ),
                html_message=html_body,
                from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', 'tom.grouptrade@gmail.com'),
                recipient_list=[email],
                fail_silently=True,
            )
            # Copy to Tom
            send_mail(
                subject=f'[New Registration] {name} — {event.title}',
                message=f'New ticket: {ticket.ticket_number}\nName: {name}\nEmail: {email}\nEvent: {event.title}',
                from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                recipient_list=['tom.grouptrade@gmail.com'],
                fail_silently=True,
            )
        except Exception:
            pass

        messages.success(request, f'Spot reserved! Your ticket {ticket.ticket_number} has been sent to {email}.')
        return redirect('ticket_detail', pk=ticket.pk)

    return redirect('event_detail', pk=pk)

@login_required
def my_tickets(request):
    tickets = EventTicket.objects.filter(
        email=request.user.email
    ).select_related('event').order_by('-registered_at')
    return render(request, 'training/my_tickets.html', {'tickets': tickets})

def ticket_detail(request, pk):
    from django.shortcuts import get_object_or_404
    ticket = get_object_or_404(EventTicket, pk=pk)
    agenda = [line.strip() for line in ticket.event.agenda.splitlines() if line.strip()]
    return render(request, 'training/ticket_detail.html', {'ticket': ticket, 'agenda': agenda})
