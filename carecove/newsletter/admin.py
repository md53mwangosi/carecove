from django.contrib import admin
from .models import Newsletter, EmailCampaign

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'language_preference', 'is_pending_approval', 'is_active', 'subscribed_at']
    list_filter = ['is_pending_approval', 'is_active', 'language_preference', 'subscribed_at']
    search_fields = ['email', 'name']
    readonly_fields = ['subscribed_at']
    
    actions = ['approve_subscriptions', 'reject_subscriptions']
    
    def approve_subscriptions(self, _request, queryset):
        queryset.update(is_pending_approval=False, is_active=True)
    approve_subscriptions.short_description = "Approve selected subscriptions"

    def reject_subscriptions(self, _request, queryset):
        queryset.update(is_pending_approval=False, is_active=False)
    reject_subscriptions.short_description = "Reject selected subscriptions"

@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ['subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['subject']