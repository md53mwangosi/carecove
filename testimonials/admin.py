
from django.contrib import admin
from django.utils.html import format_html
from .models import Testimonial

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'rating', 'status', 'is_featured', 'created_at']
    list_filter = ['status', 'rating', 'is_featured', 'created_at']
    search_fields = ['name', 'email', 'title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['approve_testimonials', 'reject_testimonials', 'feature_testimonials']
    
    fieldsets = (
        ('Customer Information', {
            'fields': ('user', 'name', 'email', 'location')
        }),
        ('Testimonial Content', {
            'fields': ('title', 'content', 'rating', 'image')
        }),
        ('Status', {
            'fields': ('status', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def approve_testimonials(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request, f"{queryset.count()} testimonials have been approved.")
    approve_testimonials.short_description = "Approve selected testimonials"
    
    def reject_testimonials(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f"{queryset.count()} testimonials have been rejected.")
    reject_testimonials.short_description = "Reject selected testimonials"
    
    def feature_testimonials(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} testimonials have been featured.")
    feature_testimonials.short_description = "Feature selected testimonials"
