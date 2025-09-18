from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Admin expense fields
    date = models.DateField(null=True, blank=True)
    paid_to = models.CharField(max_length=255, blank=True, null=True)
    charged_to = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    receipt_no = models.CharField(max_length=50, blank=True, null=True)
    sponsor = models.CharField(max_length=255, blank=True, null=True)
    amount_injected = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    bank_charges = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    running_balance = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.date} - {self.user.username} - {self.amount_paid}"

# ---------------------------
# New Sale model for user orders
class Sale(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    item = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.item} - {self.price}"

