
from django.db import models
from django.contrib.auth.models import User
from shop.models import Product, ProductVariant

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=32, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Anonymous cart {self.session_key}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cart', 'product', 'variant')

    def __str__(self):
        variant_info = f" - {self.variant.name}" if self.variant else ""
        return f"{self.product.name}{variant_info} x {self.quantity}"

    @property
    def price(self):
        if self.variant:
            return self.variant.price
        return self.product.price

    @property
    def total_price(self):
        return self.price * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    # Customer information
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField()
    
    # Billing information
    billing_first_name = models.CharField(max_length=50)
    billing_last_name = models.CharField(max_length=50)
    billing_company = models.CharField(max_length=100, blank=True)
    billing_address_1 = models.CharField(max_length=200)
    billing_address_2 = models.CharField(max_length=200, blank=True)
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100)
    billing_postal_code = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=100, default='Tanzania')
    billing_phone = models.CharField(max_length=20)
    
    # Shipping information
    shipping_first_name = models.CharField(max_length=50)
    shipping_last_name = models.CharField(max_length=50)
    shipping_company = models.CharField(max_length=100, blank=True)
    shipping_address_1 = models.CharField(max_length=200)
    shipping_address_2 = models.CharField(max_length=200, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default='Tanzania')
    
    # Order details
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Payment information
    payment_method = models.CharField(max_length=50, default='pesapal')
    payment_reference = models.CharField(max_length=100, blank=True)
    pesapal_order_tracking_id = models.CharField(max_length=100, blank=True)
    pesapal_merchant_reference = models.CharField(max_length=100, blank=True)
    pesapal_order_id = models.CharField(max_length=100, blank=True)
    payment_confirmation_code = models.CharField(max_length=100, blank=True)
    
    # Notes
    order_notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import random
            import string
            self.order_number = 'CC' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)

    @property
    def full_billing_address(self):
        address = f"{self.billing_address_1}"
        if self.billing_address_2:
            address += f", {self.billing_address_2}"
        address += f", {self.billing_city}, {self.billing_state} {self.billing_postal_code}, {self.billing_country}"
        return address

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        variant_info = f" - {self.variant.name}" if self.variant else ""
        return f"{self.product.name}{variant_info} x {self.quantity}"
