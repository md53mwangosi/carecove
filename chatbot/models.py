from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid

class ChatSession(models.Model):
    """Track chat sessions for users"""
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    visitor_ip = models.GenericIPAddressField(null=True, blank=True)
    session_token = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # WhatsApp integration fields
    transferred_to_whatsapp = models.BooleanField(default=False)
    whatsapp_transfer_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Chat Session {self.session_id} - {self.started_at.strftime('%Y-%m-%d %H:%M')}"
    
    def end_session(self):
        self.is_active = False
        self.ended_at = timezone.now()
        self.save()

class ChatMessage(models.Model):
    """Store individual chat messages"""
    MESSAGE_TYPES = [
        ('user', 'User Message'),
        ('bot', 'Bot Response'),
        ('system', 'System Message'),
        ('whatsapp_transfer', 'WhatsApp Transfer'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Additional metadata
    is_from_ai = models.BooleanField(default=False)
    ai_confidence = models.FloatField(null=True, blank=True)  # AI response confidence
    response_time_ms = models.IntegerField(null=True, blank=True)  # Response time in milliseconds
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."

class ChatbotFAQ(models.Model):
    """Predefined FAQ responses for common questions"""
    question = models.CharField(max_length=200)
    keywords = models.TextField(help_text="Comma-separated keywords to trigger this response")
    answer = models.TextField()
    category = models.CharField(max_length=50, choices=[
        ('products', 'Product Information'),
        ('shipping', 'Shipping & Delivery'),
        ('orders', 'Order Support'),
        ('general', 'General Information'),
        ('benefits', 'Health Benefits'),
        ('usage', 'Usage Instructions'),
    ])
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher numbers = higher priority")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'category']
        verbose_name = "Chatbot FAQ"
        verbose_name_plural = "Chatbot FAQs"
    
    def __str__(self):
        return f"{self.category}: {self.question}"

class QuickResponse(models.Model):
    """Quick response buttons for common actions"""
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True)
    action_type = models.CharField(max_length=30, choices=[
        ('faq', 'FAQ Response'),
        ('product_info', 'Product Information'),
        ('whatsapp', 'Transfer to WhatsApp'),
        ('order_status', 'Order Status'),
        ('contact', 'Contact Information'),
    ])
    action_data = models.JSONField(default=dict, blank=True)  # Store additional action data
    icon = models.CharField(max_length=50, default='fas fa-comment')  # Font Awesome icon class
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
