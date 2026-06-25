from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Product, Order, Payout

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'is_verified', 'city', 'phone']
    list_filter = ['role', 'is_verified']
    fieldsets = UserAdmin.fieldsets + (
        ('Extra', {'fields': ('role', 'phone', 'city', 'address', 'is_verified', 'cnic', 'business_name', 'profile_pic')}),
    )

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Payout)
