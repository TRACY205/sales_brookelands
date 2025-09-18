# myapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Expense
from decimal import Decimal
from django.utils import timezone
from .models import Expense, Sale




# --------------------------
# Price list for sales
# --------------------------
PRICE_LIST = {
    "Water": {
        "1L": 10,
        "1L + B": 30,
        "1L (R)": 10,
        "5L (R)": 70,
        "5L + Bottle": 150,
        "10L (R)": 130,
        "10L + Bottle": 250,
        "20L (R)": 250,
        "20L + Bottle": 500,
        "20L (Hard) + water": 1500,
    },
    "Gas": {
        "Insta Gas 6kg": 1000,
        "Insta Gas 13kg": 3500,
        "Pro Gas 6kg": 1000,
        "Pro Gas 13kg": 3500,
        "Wajiko 6kg": 1000,
        "Wajiko 13kg": 3500,
    }
}


# --------------------------
# Landing page
# --------------------------
def landing(request):
    return render(request, "landing.html")

# --------------------------
# User registration
# --------------------------
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        User.objects.create_user(username=username, password=password1)
        messages.success(request, "Account created successfully! You can now login.")
        return redirect("login")

    return render(request, "register.html")

# --------------------------
# User login
# --------------------------
from django.views.decorators.csrf import ensure_csrf_cookie

@ensure_csrf_cookie
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_superuser:
                return redirect("admin_dashboard")
            return redirect("user_dashboard")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "login.html")

# --------------------------
# Logout
# --------------------------
def logout_view(request):
    logout(request)
    return redirect("login")

# --------------------------
# User dashboard
# --------------------------
from django.utils import timezone
from decimal import Decimal
import json

@login_required
def user_dashboard(request):
    if request.method == "POST":
        category = request.POST.get("category")
        item = request.POST.get("item") or request.POST.get("local_item")
        quantity = request.POST.get("quantity")
        price = request.POST.get("price")
        payment_method = request.POST.get("payment_method")

        if not category or not item or not quantity or not price or not payment_method:
            messages.error(request, "⚠️ Please fill all required fields.")
            return redirect("user_dashboard")

        Expense.objects.create(
            user=request.user,
            category=category,
            item=item,
            quantity=int(quantity),
            price=Decimal(price),
            payment_method=payment_method,
            date=timezone.now()
        )
        messages.success(request, "✅ Order submitted successfully!")
        return redirect("user_dashboard")

    expenses = Expense.objects.filter(user=request.user).order_by("-date")
    
    return render(request, "user_dashboard.html", {
        "expenses": expenses,
        "PRICE_LIST_JSON": json.dumps(PRICE_LIST)  # <--- pass as JSON string
    })








# --------------------------
# Admin dashboard
# --------------------------

from .models import Expense, Sale
from django.db.models import Sum

def admin_dashboard(request):
    # Admin expenses
    expenses = Expense.objects.all().order_by("-date")
    total_expenses = expenses.aggregate(total=Sum("amount_paid"))["total"] or 0

    # User sales/orders
    sales = Sale.objects.all().order_by("-date")
    total_sales = sales.aggregate(total=Sum("price"))["total"] or 0

    context = {
        "expenses": expenses,
        "total_expenses": total_expenses,
        "sales": sales,
        "total_sales": total_sales,
    }
    return render(request, "admin_dashboard.html", context)



# --------------------------
# Add sale (user)
# --------------------------
@login_required
def add_sale(request):
    if request.method == "POST":
        category = request.POST.get("category")
        item = request.POST.get("item")
        quantity = request.POST.get("quantity")
        payment_method = request.POST.get("payment_method")

        try:
            quantity = int(quantity)
        except:
            quantity = 0

        unit_price = PRICE_LIST.get(item)
        if category and item and quantity > 0 and unit_price is not None and payment_method:
            Expense.objects.create(
                user=request.user,
                category=category,
                item=item,
                quantity=quantity,
                price=unit_price * quantity,
                payment_method=payment_method
            )
            return redirect("user_dashboard")

    return render(request, "add_sale.html", {"PRICE_LIST": PRICE_LIST})

# --------------------------
# Add expense (admin)
# --------------------------
@login_required
def add_expense(request):
    if request.method == "POST":
        date = request.POST.get("date")
        paid_to = request.POST.get("paid_to")
        charged_to = request.POST.get("charged_to")
        description = request.POST.get("description")
        receipt_no = request.POST.get("receipt_no")
        sponsor = request.POST.get("sponsor")
        amount_injected = request.POST.get("amount_injected")
        amount_paid = request.POST.get("amount_paid")
        bank_charges = request.POST.get("bank_charges")
        running_balance = request.POST.get("running_balance")

        if not date or not paid_to or not charged_to or not description or not amount_injected or not amount_paid:
            messages.error(request, "Please fill all required fields.")
            return redirect("add_expense")

        try:
            amount_injected = float(amount_injected)
            amount_paid = float(amount_paid)
            bank_charges = float(bank_charges) if bank_charges else 0
            running_balance = float(running_balance) if running_balance else 0
        except ValueError:
            messages.error(request, "Amounts must be numbers.")
            return redirect("add_expense")

        Expense.objects.create(
            user=request.user,
            date=date,
            paid_to=paid_to,
            charged_to=charged_to,
            description=description,
            receipt_no=receipt_no,
            sponsor=sponsor,
            amount_injected=amount_injected,
            amount_paid=amount_paid,
            bank_charges=bank_charges,
            running_balance=running_balance
        )

        messages.success(request, "Expense added successfully!")
        return redirect("admin_dashboard")

    return render(request, "add_expense.html")

# --------------------------
# Upload expenses (Excel/CSV)
# --------------------------
@login_required
def upload_expense(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        # handle Excel/CSV upload logic here
        messages.success(request, "Expenses uploaded successfully!")
        return redirect("admin_dashboard")
    return render(request, "upload_expense.html")

# --------------------------
# Admin PDF reports
# --------------------------
# myapp/views.py
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from .models import Expense

def admin_expenses_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expenses_report.pdf"'

    # Create PDF
    pdf = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    # Table header
    data = [
        [
            "Date", "Paid To", "Charged To", "Description",
            "Receipt No", "Sponsor", "Amount Injected",
            "Amount Paid", "Bank Charges", "Running Balance"
        ]
    ]

    # Fetch expense data from the database
    expenses = Expense.objects.all()  # You can filter if needed
    running_balance = 0
    for exp in expenses:
        injected = exp.amount_injected or 0
        paid = exp.amount_paid or 0
        charges = exp.bank_charges or 0
        running_balance += injected - paid - charges

        data.append([
            exp.date.strftime("%d-%m-%Y") if exp.date else "",
            exp.paid_to,
            exp.charged_to,
            exp.description,
            exp.receipt_no,
            exp.sponsor,
            f"{injected:.2f}",
            f"{paid:.2f}",
            f"{charges:.2f}",
            f"{running_balance:.2f}"
        ])

    # Create table
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))

    elements.append(table)
    pdf.build(elements)
    return response

