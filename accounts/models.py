
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    birth_date = models.DateField(blank=True, null=True)
    
    # Default addresses
    default_billing_address_1 = models.CharField(max_length=200, blank=True)
    default_billing_address_2 = models.CharField(max_length=200, blank=True)
    default_billing_city = models.CharField(max_length=100, blank=True)
    default_billing_state = models.CharField(max_length=100, blank=True)
    default_billing_postal_code = models.CharField(max_length=20, blank=True)
    default_billing_country = models.CharField(max_length=100, default='Tanzania')
    
    default_shipping_address_1 = models.CharField(max_length=200, blank=True)
    default_shipping_address_2 = models.CharField(max_length=200, blank=True)
    default_shipping_city = models.CharField(max_length=100, blank=True)
    default_shipping_state = models.CharField(max_length=100, blank=True)
    default_shipping_postal_code = models.CharField(max_length=20, blank=True)
    default_shipping_country = models.CharField(max_length=100, default='Tanzania')
    
    # Preferences
    preferred_language = models.CharField(max_length=2, choices=[('en', 'English'), ('sw', 'Swahili')], default='en')
    receive_newsletter = models.BooleanField(default=True)
    receive_order_updates = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

class Address(models.Model):
    ADDRESS_TYPES = [
        ('billing', 'Billing'),
        ('shipping', 'Shipping'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    type = models.CharField(max_length=10, choices=ADDRESS_TYPES)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company = models.CharField(max_length=100, blank=True)
    address_1 = models.CharField(max_length=200)
    address_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Tanzania')
    phone = models.CharField(max_length=20, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'type', 'is_default')

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.type}"
