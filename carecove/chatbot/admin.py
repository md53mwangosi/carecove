from django.contrib import admin
from .models import ChatSession, ChatMessage, ChatbotFAQ, QuickResponse

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'visitor_ip', 'is_active', 'transferred_to_whatsapp', 'started_at']
    list_filter = ['is_active', 'transferred_to_whatsapp', 'started_at']
    search_fields = ['session_id', 'user__username', 'visitor_ip']
    readonly_fields = ['session_id', 'started_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'message_type', 'content_preview', 'is_from_ai', 'timestamp']
    list_filter = ['message_type', 'is_from_ai', 'timestamp']
    search_fields = ['content', 'session__session_id']
    readonly_fields = ['timestamp']
    
    def content_preview(self, obj):
        return obj.content[:100] + "..." if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

@admin.register(ChatbotFAQ)
class ChatbotFAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'priority', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'keywords', 'answer']
    list_editable = ['priority', 'is_active']
    
    fieldsets = (
        (None, {
            'fields': ('question', 'category', 'keywords')
        }),
        ('Response', {
            'fields': ('answer',)
        }),
        ('Settings', {
            'fields': ('priority', 'is_active')
        }),
    )

@admin.register(QuickResponse)
class QuickResponseAdmin(admin.ModelAdmin):
    list_display = ['title', 'action_type', 'is_active', 'order']
    list_filter = ['action_type', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_active']
