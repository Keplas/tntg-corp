from django.db import models
from accounts.models import CustomUser


class TrainingProgram(models.Model):
    CATEGORY_CHOICES = [
        ('farming',    'Modern & Tech Farming'),
        ('enterprise', 'Trade & E-Commerce'),
        ('trade',      'Import & Export Operations'),
    ]
    title            = models.CharField(max_length=300)
    category         = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description      = models.TextField()
    thumbnail        = models.ImageField(upload_to='training/', blank=True, null=True)
    video_url        = models.URLField(blank=True)
    duration_hours   = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    certificate_fee  = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    is_free          = models.BooleanField(default=True)
    is_active        = models.BooleanField(default=True)
    created_at       = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Enrollment(models.Model):
    STATUS = [
        ('enrolled',              'Enrolled'),
        ('in_progress',           'In Progress'),
        ('completed',             'Completed'),
        ('certificate_requested', 'Certificate Requested'),
        ('certified',             'Certified'),
    ]
    user              = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrollments')
    program           = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='enrollments')
    status            = models.CharField(max_length=30, choices=STATUS, default='enrolled')
    progress_percent  = models.IntegerField(default=0)
    quiz_score        = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    certificate_paid  = models.BooleanField(default=False)
    certificate_issued= models.BooleanField(default=False)
    enrolled_at       = models.DateTimeField(auto_now_add=True)
    completed_at      = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} — {self.program.title}"


class TVProgram(models.Model):
    title              = models.CharField(max_length=300)
    description        = models.TextField()
    thumbnail          = models.ImageField(upload_to='tv/', blank=True, null=True)
    thumbnail_url      = models.URLField(blank=True, help_text="External thumbnail URL (Unsplash etc.)")
    video_url          = models.URLField(blank=True)
    broadcast_schedule = models.CharField(max_length=200, blank=True)
    category           = models.CharField(max_length=100, blank=True)
    is_live            = models.BooleanField(default=False)
    is_active          = models.BooleanField(default=True)
    created_at         = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


import uuid

class TrainingEvent(models.Model):
    CATEGORY = [
        ('shopping',    'T&TG Shopping Platform'),
        ('loyalty',     'Loyalty & Rewards'),
        ('trade',       'Import & Export Trade'),
        ('forex',       'Live Forex & Currency'),
        ('onboarding',  'Platform Onboarding'),
        ('coffee',      'Coffee Knowledge'),
    ]
    title           = models.CharField(max_length=300)
    category        = models.CharField(max_length=20, choices=CATEGORY)
    description     = models.TextField()
    agenda          = models.TextField(blank=True, help_text="Line-by-line agenda items")
    event_date      = models.DateTimeField()
    duration_mins   = models.IntegerField(default=60)
    capacity        = models.IntegerField(default=100)
    is_free         = models.BooleanField(default=True)
    price_points    = models.IntegerField(default=0, help_text="Cost in T&TG Loyalty Points (0 = free)")
    video_url       = models.URLField(blank=True, help_text="YouTube/stream link unlocked after registration")
    thumbnail_url   = models.URLField(blank=True)
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)

    @property
    def spots_taken(self):
        return self.tickets.filter(status='confirmed').count()

    @property
    def spots_left(self):
        return max(0, self.capacity - self.spots_taken)

    @property
    def is_full(self):
        return self.spots_left == 0

    def __str__(self):
        return self.title


class EventTicket(models.Model):
    STATUS = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('attended',  'Attended'),
    ]
    ticket_number   = models.CharField(max_length=20, unique=True, editable=False)
    event           = models.ForeignKey(TrainingEvent, on_delete=models.CASCADE, related_name='tickets')
    user            = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='event_tickets', null=True, blank=True)
    name            = models.CharField(max_length=200)
    email           = models.EmailField()
    SPOT_TYPE = [('in_person','Reserve a Spot (In-Person)'),('online','Online Spot (Virtual)')]
    spot_type       = models.CharField(max_length=20, choices=SPOT_TYPE, default='online')
    status          = models.CharField(max_length=20, choices=STATUS, default='confirmed')
    registered_at   = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = 'TKT-' + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ticket_number} — {self.name} — {self.event.title}"
