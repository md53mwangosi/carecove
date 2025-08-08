
from django.contrib import admin
from django.utils.html import format_html
from .models import Cart, CartItem, Order, OrderItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'total_price', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'session_key']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'variant', 'quantity', 'price', 'total_price']
    list_filter = ['created_at']
    search_fields = ['product__name', 'cart__user__username']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'variant', 'quantity', 'price', 'total']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'user', 'email', 'status', 'payment_status', 'total', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'user__username', 'email', 'billing_first_name', 'billing_last_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'email', 'status', 'payment_status')
        }),
        ('Billing Address', {
            'fields': (
                'billing_first_name', 'billing_last_name', 'billing_company',
                'billing_address_1', 'billing_address_2', 'billing_city',
                'billing_state', 'billing_postal_code', 'billing_country', 'billing_phone'
            )
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_first_name', 'shipping_last_name', 'shipping_company',
                'shipping_address_1', 'shipping_address_2', 'shipping_city',
                'shipping_state', 'shipping_postal_code', 'shipping_country'
            )
        }),
        ('Order Totals', {
            'fields': ('subtotal', 'shipping_cost', 'tax_amount', 'total')
        }),
        ('Payment Information', {
            'fields': ('payment_method', 'payment_reference')
        }),
        ('Notes', {
            'fields': ('order_notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='processing')
        self.message_user(request, f"{queryset.count()} orders marked as processing.")
    mark_as_processing.short_description = "Mark selected orders as processing"
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')
        self.message_user(request, f"{queryset.count()} orders marked as shipped.")
    mark_as_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')
        self.message_user(request, f"{queryset.count()} orders marked as delivered.")
    mark_as_delivered.short_description = "Mark selected orders as delivered"
