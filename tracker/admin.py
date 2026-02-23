from django.contrib import admin
from .models import Category, Item, Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'display_name')
	search_fields = ('user__username', 'user__email', 'display_name')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ('name', 'user')
	search_fields = ('name', 'user__username', 'user__email')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
	list_display = ('name', 'user', 'category', 'purchase_price', 'estimated_value', 'condition', 'purchase_date')
	search_fields = ('name', 'user__username', 'user__email', 'category__name')
	list_filter = ('condition', 'category')
