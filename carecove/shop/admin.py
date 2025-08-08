from django.contrib import admin
from django.utils.html import format_html
from django.core.mail import mail_admins
from .models import Category, Product, ProductImage, ProductVariant, ProductReview

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'sort_order']

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['name', 'sku', 'price', 'stock_quantity', 'weight', 'is_active']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'product_type', 'price', 'stock_quantity', 'is_active', 'is_featured']
    list_filter = ['category', 'product_type', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    inlines = [ProductImageInline, ProductVariantInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'product_type', 'description')
        }),
        ('Pricing', {
            'fields': ('price', 'compare_at_price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('sku', 'stock_quantity', 'track_inventory', 'allow_backorders')
        }),
        ('Product Details', {
            'fields': ('weight', 'origin', 'ingredients', 'benefits', 'usage_instructions')
        }),
        ('SEO & Status', {
            'fields': ('meta_title', 'meta_description', 'is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['product', 'user', 'rating', 'title', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__username', 'title', 'review']
    actions = ['approve_reviews', 'reject_reviews']
    readonly_fields = ['created_at']
    
    def approve_reviews(self, request, queryset):
        approved_count = queryset.filter(is_approved=False).update(is_approved=True)
        self.message_user(request, f"{approved_count} reviews have been approved and are now visible.")
    approve_reviews.short_description = "Approve selected reviews"
    
    def reject_reviews(self, request, queryset):
        rejected_count = queryset.filter(is_approved=True).update(is_approved=False)
        self.message_user(request, f"{rejected_count} reviews have been rejected and hidden.")
    reject_reviews.short_description = "Reject selected reviews"
    
    def save_model(self, request, obj, form, change):
        # Send notification when a review is first created
        if not change and not obj.is_approved:
            try:
                mail_admins(
                    'New Product Review Pending Approval',
                    f'A new product review has been submitted and requires approval:\n\n'
                    f'Product: {obj.product.name}\n'
                    f'User: {obj.user.username} ({obj.user.email})\n'
                    f'Rating: {obj.rating} stars\n'
                    f'Title: {obj.title}\n'
                    f'Review: {obj.review[:200]}...\n\n'
                    f'Please review and approve/reject this review in the admin panel.',
                    fail_silently=True,
                )
            except Exception:
                pass  # Fail silently if email can't be sent
        
        super().save_model(request, obj, form, change)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image_preview', 'alt_text', 'is_primary', 'sort_order']
    list_filter = ['is_primary', 'product']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;">', obj.image.url)
        return "No Image"
    image_preview.short_description = "Preview"