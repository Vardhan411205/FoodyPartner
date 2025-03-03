from django.contrib import admin
# Register your models here
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'customer_email', 'restaurant_name', 'order_type', 'total_amount', 'status', 'booking_date']
    list_filter = ['status', 'order_type', 'booking_date']
    search_fields = ['order_id', 'customer_email', 'restaurant_name']
    readonly_fields = ['created_at', 'updated_at']
