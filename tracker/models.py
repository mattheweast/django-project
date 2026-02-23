from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


class Profile(models.Model):
	class Currency(models.TextChoices):
		USD = 'USD', 'US Dollar (USD)'
		GBP = 'GBP', 'British Pound (GBP)'
		EUR = 'EUR', 'Euro (EUR)'
		CAD = 'CAD', 'Canadian Dollar (CAD)'
		AUD = 'AUD', 'Australian Dollar (AUD)'

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
	display_name = models.CharField(max_length=100, blank=True)
	bio = models.TextField(blank=True)
	preferred_currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)

	def __str__(self):
		return self.display_name or self.user.username


class Category(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
	name = models.CharField(max_length=100)

	class Meta:
		ordering = ['name']
		constraints = [
			models.UniqueConstraint(fields=['user', 'name'], name='unique_category_per_user')
		]

	def __str__(self):
		return self.name


class Item(models.Model):
	class Condition(models.TextChoices):
		NEW = 'new', 'New'
		LIKE_NEW = 'like_new', 'Like New'
		GOOD = 'good', 'Good'
		FAIR = 'fair', 'Fair'
		POOR = 'poor', 'Poor'

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='items')
	category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='items')
	name = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	condition = models.CharField(max_length=20, choices=Condition.choices, default=Condition.GOOD)
	purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
	estimated_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
	purchase_date = models.DateField(null=True, blank=True)
	photo = models.ImageField(upload_to='item_photos/', null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	@property
	def gain_loss(self):
		if self.estimated_value is None:
			return None
		return self.estimated_value - self.purchase_price

	@property
	def depreciation_percent(self):
		if self.estimated_value is None or self.purchase_price == 0:
			return None
		return (self.gain_loss / self.purchase_price) * Decimal('100')

	def __str__(self):
		return self.name
