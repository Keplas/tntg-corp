from django.db import models
from accounts.models import CustomUser

class InsurancePolicy(models.Model):
    POLICY_TYPES = [
        ('health','Health Insurance'),
        ('trade','Trade Insurance'),
        ('cargo','Cargo Insurance'),
        ('business','Business Insurance'),
        ('life','Life Insurance'),
    ]
    STATUS = [('active','Active'),('pending','Pending'),('expired','Expired'),('cancelled','Cancelled')]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='insurance_policies')
    policy_type = models.CharField(max_length=20, choices=POLICY_TYPES)
    policy_number = models.CharField(max_length=50, unique=True)
    coverage_amount = models.DecimalField(max_digits=14, decimal_places=2)
    premium = models.DecimalField(max_digits=10, decimal_places=2)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.policy_number} - {self.user.username}"

class BrokerageAccount(models.Model):
    ACCOUNT_TYPES = [('forex','Forex'),('stocks','Stocks'),('commodities','Commodities'),('crypto','Cryptocurrency')]
    STATUS = [('active','Active'),('pending','Pending'),('suspended','Suspended')]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='brokerage_accounts')
    account_number = models.CharField(max_length=50, unique=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    currency = models.CharField(max_length=5, default='USD')
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.account_number} - {self.user.username}"

class ForexRate(models.Model):
    from_currency = models.CharField(max_length=5)
    to_currency = models.CharField(max_length=5)
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.from_currency}/{self.to_currency} = {self.rate}"

class ContactInquiry(models.Model):
    INQUIRY_TYPES = [('general','General'),('partnership','Partnership'),('support','Support'),('investment','Investment')]
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES, default='general')
    subject = models.CharField(max_length=300)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"
