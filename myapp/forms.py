from django import forms
from .models import Sale

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["category", "item", "quantity", "price", "payment_method"]
        # ⚠️ notice: no "date" field here, since it's auto-generated in your model


from django import forms
from .models import Expense

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
