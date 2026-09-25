"""
T&TG Trade Corporation — Custom Signup Form
Extends allauth signup with extra fields
"""
from allauth.account.forms import SignupForm
from django import forms


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=50, required=True, label='First Name')
    last_name  = forms.CharField(max_length=50, required=True, label='Last Name')
    phone      = forms.CharField(max_length=20, required=False, label='Phone Number')
    country    = forms.ChoiceField(choices=[
        ('', 'Select your country'),
        ('CA', 'Canada'),
        ('US', 'United States'),
        ('UG', 'Uganda'),
        ('KE', 'Kenya'),
        ('NL', 'Netherlands'),
        ('JP', 'Japan'),
        ('other', 'Other'),
    ], required=True, label='Country')

    field_order = ['first_name', 'last_name', 'email', 'username', 'phone', 'country', 'password1', 'password2']

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name  = self.cleaned_data.get('last_name', '')
        user.phone      = self.cleaned_data.get('phone', '')
        user.country    = self.cleaned_data.get('country', '')
        user.save()
        return user
