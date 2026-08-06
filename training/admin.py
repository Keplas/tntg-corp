from django.contrib import admin
from .models import TrainingProgram, TVProgram, TrainingEvent, EventTicket


@admin.register(TrainingEvent)
class TrainingEventAdmin(admin.ModelAdmin):
    list_display  = ['title', 'category', 'event_date', 'capacity', 'spots_taken', 'is_free', 'is_active']
    list_filter   = ['category', 'is_free', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['is_active']
    fields = ['title', 'category', 'description', 'agenda', 'event_date',
              'duration_mins', 'capacity', 'is_free', 'price_points',
              'video_url', 'thumbnail_url', 'is_active']


@admin.register(EventTicket)
class EventTicketAdmin(admin.ModelAdmin):
    list_display  = ['ticket_number', 'name', 'email', 'event', 'spot_type', 'status', 'registered_at']
    list_filter   = ['status', 'spot_type', 'event']
    search_fields = ['ticket_number', 'name', 'email']
    readonly_fields = ['ticket_number', 'registered_at']


@admin.register(TrainingProgram)
class TrainingProgramAdmin(admin.ModelAdmin):
    list_display  = ['title', 'category', 'duration', 'is_active']
    list_filter   = ['category', 'is_active']
    search_fields = ['title']


@admin.register(TVProgram)
class TVProgramAdmin(admin.ModelAdmin):
    list_display  = ['title', 'category', 'thumbnail_url', 'is_active']
    list_filter   = ['category', 'is_active']
    search_fields = ['title']
