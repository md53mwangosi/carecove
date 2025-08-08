
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class AdminActivityLog(models.Model):
    """Track admin activities for audit purposes"""
    ACTION_TYPES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('view', 'Viewed'),
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('export', 'Exported'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_TYPES)
    model_name = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} {self.action} {self.model_name} at {self.timestamp}"

class AdminNotification(models.Model):
    """System notifications for admin users"""
    NOTIFICATION_TYPES = [
        ('order', 'New Order'),
        ('review', 'New Review'),
        ('testimonial', 'New Testimonial'),
        ('low_stock', 'Low Stock Alert'),
        ('system', 'System Alert'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class AdminSettings(models.Model):
    """Store admin panel settings"""
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Admin Setting"
        verbose_name_plural = "Admin Settings"
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"
