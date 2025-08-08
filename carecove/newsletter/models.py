from django.db import models

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True)
    language_preference = models.CharField(
        max_length=2, 
        choices=[('en', 'English'), ('sw', 'Swahili')], 
        default='en'
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    is_pending_approval = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-subscribed_at']

class EmailCampaign(models.Model):
    subject = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(
        max_length=10, 
        choices=[('draft', 'Draft'), ('sent', 'Sent'), ('scheduled', 'Scheduled')], 
        default='draft'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject