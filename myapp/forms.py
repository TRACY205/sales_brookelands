from django import forms
from .models import Sale, Expense


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = [
            "date",
            "paid_to",
            "charged_to",
            "description",
            "receipt_no",
            "sponsor",
            "amount_injected",
            "amount_paid",
            "bank_charges",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),  # HTML date picker
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
        model = Sale
        fields = [
            "category",
            "item",
            "quantity",
            "price",
            "payment_method",
            "payment_status",
            "date",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
