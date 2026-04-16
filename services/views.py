from django.shortcuts import render
from .models import ForexRate, InsurancePolicy, BrokerageAccount
from django.contrib.auth.decorators import login_required

def insurance(request):
    return render(request, 'services/insurance.html')

def brokerage(request):
    rates = ForexRate.objects.all()
    return render(request, 'services/brokerage.html', {'rates': rates})

def forex(request):
    rates = ForexRate.objects.all()
    return render(request, 'services/forex.html', {'rates': rates})

def financial_services(request):
    return render(request, 'services/financial_services.html')
