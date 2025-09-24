from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
# Sale model for user orders
class Sale(models.Model):
    PAYMENT_METHOD = [
        ("Cash", "Cash"),
        ("MPesa", "MPesa"),
    ]

    PAYMENT_STATUS = [
        ("Paid", "Paid"),
        ("Delivery", "Delivery"),
        ("Not Paid", "Not Paid"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
    item = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD)
    date = models.DateField(default=timezone.now)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="Not Paid")

    def __str__(self):
        return f"{self.user.username} - {self.item} - {self.price} ({self.payment_status})"

