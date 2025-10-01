from django import forms
from .models import Expense, Sale

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            "date",
            "paid_to",
            "charges_account",
            "description",
            "received_amount",
            "bank_charges",
            "amount_paid",
            "cumulative_balance",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }


class SaleForm(forms.ModelForm):
    PAYMENT_STATUS_CHOICES = [
        ("Paid", "💰 Paid"),
        ("Delivery", "✅ Delivery"),
        ("Not Paid", "❌ Not Paid"),
    ]

    payment_status = forms.ChoiceField(
        choices=PAYMENT_STATUS_CHOICES,
        widget=forms.RadioSelect,
        required=True,
    )

    class Meta:
        model = Sale  # ⚠ Must be Sale, not Expense
        fields = [
            "category",
            "item",
            "quantity",
            "price",
            "payment_method",
            "payment_status",
            "delivery_place",  # only if model has it
            "date",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
