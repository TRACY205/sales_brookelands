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
from .models import Expense, Sale
from decimal import Decimal
from django.utils import timezone
import json

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
        is_admin_portal = request.POST.get("is_admin_portal")  # Optional hidden input from admin button
        user = authenticate(request, username=username, password=password)
        if user:
            if is_admin_portal and not user.is_superuser:
                messages.error(request, "🚫 Unauthorized access to Admin portal.")
                return redirect("landing")
            
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

        Sale.objects.create(
            user=request.user,
            category=category,
            item=item,
            quantity=int(quantity),
            price=Decimal(price),
            payment_method=payment_method
        )
        messages.success(request, "✅ Order submitted successfully!")
        return redirect("user_dashboard")

    sales = Sale.objects.filter(user=request.user).order_by("-date")
    
    return render(request, "user_dashboard.html", {
        "sales": sales,
        "PRICE_LIST_JSON": json.dumps(PRICE_LIST)
    })

# --------------------------
# Admin dashboard
# --------------------------
@login_required
def admin_dashboard(request):
    # Prevent unauthorized access
    if not request.user.is_superuser:
        messages.error(request, "🚫 Unauthorized access.")
        return redirect("user_dashboard")

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
from decimal import Decimal

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
            total_price = Decimal(unit_price) * quantity

            # ✅ Store clean decimal value in DB
            Sale.objects.create(
                user=request.user,
                category=category,
                item=item,
                quantity=quantity,
                price=total_price,
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






# myapp/views.py
from django.http import HttpResponse
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from .models import Expense, Sale

# ------------------- Excel Expenses -------------------
def admin_expenses_excel(request):
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="expenses_report.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = "Expenses Report"

    headers = [
        "Date", "Paid To", "Charged To", "Description",
        "Receipt No", "Sponsor", "Amount Injected",
        "Amount Paid", "Bank Charges", "Running Balance"
    ]
    ws.append(headers)

    expenses = Expense.objects.all().order_by("date")

    running_balance = 0
    total_injected = 0
    total_paid = 0
    total_charges = 0

    for exp in expenses:
        injected = getattr(exp, 'amount_injected', 0) or 0
        paid = getattr(exp, 'amount_paid', 0) or 0
        charges = getattr(exp, 'bank_charges', 0) or 0

        running_balance += injected - paid - charges
        total_injected += injected
        total_paid += paid
        total_charges += charges
        ws.append([
    exp.date.strftime("%d/%m/%y") if exp.date else "",  # <-- comma added here
    getattr(exp, 'paid_to', ''),
    getattr(exp, 'charged_to', ''),
    getattr(exp, 'description', ''),
    getattr(exp, 'receipt_no', ''),
    getattr(exp, 'sponsor', ''),
    float(injected),
    float(paid),
    float(charges),
    float(running_balance),
])


        
  
        

    ws.append([
        "", "", "", "TOTALS", "", "",
        float(total_injected),
        float(total_paid),
        float(total_charges),
        float(running_balance),
    ])

    wb.save(response)
    return response

# ------------------- PDF Sales -------------------
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from .models import Sale

def admin_sales_pdf(request):
    # Create HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="brookelands_sales_report.pdf"'

    # Setup PDF document
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    title_style.alignment = 1  # center

    # Title
    elements.append(Paragraph("Brookelands Sales Report", title_style))
    elements.append(Spacer(1, 20))  # Space below title

    # Table headers
    data = [["Date", "Item", "Quantity", "Price"]]

    # Table content
    sales = Sale.objects.all().order_by("date")
    total_price = 0
    for s in sales:
        data.append([
          s.date.strftime("%d/%m/%y"),
            s.item,
            s.quantity,
            float(s.price),
        ])
        total_price += float(s.price)

    # Add totals row
    data.append(["", "", "TOTAL", total_price])

    # Create table
    table = Table(data, colWidths=[100, 200, 80, 80])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.gray),  # Header row
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (-2,-1), (-1,-1), colors.lightgrey),  # Totals row
        ('FONTNAME', (-2,-1), (-1,-1), 'Helvetica-Bold'),
    ]))

    elements.append(table)

    # Build PDF
    doc.build(elements)
    return response
