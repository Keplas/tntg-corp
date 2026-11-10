from django import forms
from .models import ServiceBooking


class BookingForm(forms.ModelForm):
    class Meta:
        model  = ServiceBooking
        fields = [
            'client_type', 'full_name', 'email', 'phone', 'company_name',
            'problem_description', 'urgency',
        ]
        widgets = {
            'client_type': forms.RadioSelect(),
            'urgency':     forms.RadioSelect(),
            'problem_description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Describe the issue or task you need help with. '
                               'The more detail you provide, the better we can assist you.',
            }),
            'full_name':    forms.TextInput(attrs={'placeholder': 'Full name'}),
            'email':        forms.EmailInput(attrs={'placeholder': 'Email address'}),
            'phone':        forms.TextInput(attrs={'placeholder': 'Phone number (optional)'}),
            'company_name': forms.TextInput(attrs={'placeholder': 'Company name (if applicable)'}),
        }
        labels = {
            'client_type': 'I am booking as a',
            'full_name':   'Full Name',
            'problem_description': 'Describe Your Request',
        }
