from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings as djsettings
from django.utils import timezone

from .models import Department, ProfessionalProfile, ServicePackage, ServiceBooking
from .forms import BookingForm


def pro_home(request):
    """Professional services marketplace landing page."""
    departments = Department.objects.filter(is_active=True)
    ctx = {'departments': departments}
    return render(request, 'professionals/pro_home.html', ctx)


def pro_department(request, slug):
    """Department page — professionals + service packages."""
    dept         = get_object_or_404(Department, slug=slug, is_active=True)
    packages     = dept.packages.filter(is_active=True)
    professionals = dept.professionals.filter(is_available=True)
    ctx = {
        'dept':          dept,
        'packages':      packages,
        'professionals': professionals,
        'departments':   Department.objects.filter(is_active=True),
    }
    return render(request, 'professionals/pro_department.html', ctx)


def pro_book(request, pkg_id):
    """Booking form — client describes problem and pays."""
    package = get_object_or_404(ServicePackage, pk=pkg_id, is_active=True)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.package  = package
            booking.amount   = package.price
            booking.currency = package.currency
            booking.payment_status = 'paid'   # TODO: wire Moneris; treat as paid for now
            booking.paid_at  = timezone.now()
            booking.status   = 'new'
            booking.save()

            # ── Email to client ──────────────────────────────────────────────
            try:
                send_mail(
                    subject=f'Booking Confirmed — {package.department} Service | T&TG Trade Corporation',
                    message=(
                        f'Dear {booking.full_name},\n\n'
                        f'Thank you for booking a professional service with T&TG Trade Corporation.\n\n'
                        f'BOOKING DETAILS\n'
                        f'  Reference:   {booking.ref()}\n'
                        f'  Department:  {package.department}\n'
                        f'  Service:     {package.name}\n'
                        f'  Amount Paid: {booking.currency} {booking.amount:,.2f}\n\n'
                        f'WHAT HAPPENS NEXT\n'
                        f'A qualified professional from our {package.department} team will contact '
                        f'you directly at {booking.email} within 1–2 business days to begin '
                        f'working on your request.\n\n'
                        f'If you have any questions in the meantime, contact us at:\n'
                        f'  Email: tom.grouptrade@gmail.com\n'
                        f'  Phone: +1 (416) 832 3512\n\n'
                        f'T&TG Trade Corporation\n'
                        f'9 Summerbridge Rd, Toronto, ON M1G 1L8, Canada'
                    ),
                    from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                    recipient_list=[booking.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            # ── Notification to HQ ───────────────────────────────────────────
            try:
                send_mail(
                    subject=f'[NEW BOOKING] {booking.ref()} — {package.department}: {package.name}',
                    message=(
                        f'A new professional service booking has been received.\n\n'
                        f'BOOKING REFERENCE: {booking.ref()}\n'
                        f'  Department:  {package.department}\n'
                        f'  Service:     {package.name} ({package.get_service_type_display()})\n'
                        f'  Amount:      {booking.currency} {booking.amount:,.2f}\n'
                        f'  Urgency:     {booking.get_urgency_display()}\n\n'
                        f'CLIENT\n'
                        f'  Name:    {booking.full_name}\n'
                        f'  Email:   {booking.email}\n'
                        f'  Phone:   {booking.phone or "—"}\n'
                        f'  Type:    {booking.get_client_type_display()}\n'
                        f'  Company: {booking.company_name or "—"}\n\n'
                        f'PROBLEM DESCRIPTION\n'
                        f'{booking.problem_description}\n\n'
                        f'ACTION REQUIRED: Assign a professional and contact the client.\n'
                        f'Admin: https://tomtradecorp.com/admin/professionals/servicebooking/{booking.pk}/change/'
                    ),
                    from_email=getattr(djsettings, 'DEFAULT_FROM_EMAIL', ''),
                    recipient_list=['tom.grouptrade@gmail.com'],
                    fail_silently=True,
                )
            except Exception:
                pass

            return redirect('pro_confirmation', pk=booking.pk)
    else:
        form = BookingForm()

    ctx = {
        'package': package,
        'form':    form,
    }
    return render(request, 'professionals/pro_book.html', ctx)


def pro_confirmation(request, pk):
    """Booking confirmation page."""
    booking = get_object_or_404(ServiceBooking, pk=pk)
    return render(request, 'professionals/pro_confirmation.html', {'booking': booking})
