# myapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io

from .models import Sale

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
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:   # admin/staff
                return redirect("admin_dashboard")
            else:
                return redirect("user_dashboard")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")


# --------------------------
# User logout
# --------------------------
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("landing")


# --------------------------
# Price list (backend-secured)
# --------------------------
PRICE_LIST = {
    "20L": 250,
    "10L": 150,
    "5L": 80,
    "1L (Pack)": 50,
    "500ML (Pack)": 30,
}


# --------------------------
# User dashboard
# --------------------------
@login_required
def user_dashboard(request):
    if request.method == "POST":
        category = request.POST.get("category")
        item = request.POST.get("item")
        quantity = request.POST.get("quantity")

        # ✅ Force price from backend
        price = PRICE_LIST.get(item)

        if category and item and quantity and price:
            Sale.objects.create(
                user=request.user,
                category=category,
                item=item,
                quantity=int(quantity),
                price=price
            )
            messages.success(request, "Order submitted successfully!")
            return redirect("user_dashboard")
        else:
            messages.error(request, "Please fill all fields correctly.")

    sales = Sale.objects.filter(user=request.user).order_by("-date")
    return render(request, "user_dashboard.html", {"sales": sales, "PRICE_LIST": PRICE_LIST})


# --------------------------
# Admin dashboard
# --------------------------
@login_required
def admin_dashboard(request):
    sales = Sale.objects.all().order_by("-date")

    # ✅ Use price * quantity
    sales_with_total = sales.annotate(
        total_price=ExpressionWrapper(F("price") * F("quantity"), output_field=DecimalField())
    )
    total_amount = sales_with_total.aggregate(total=Sum("total_price"))["total"] or 0

    context = {
        "sales": sales_with_total,
        "total_amount": total_amount,
    }
    return render(request, "admin_dashboard.html", context)


# --------------------------
# Admin PDF report
# --------------------------
@login_required
def admin_dashboard_pdf(request):
    sales = Sale.objects.all().annotate(
        total_price=ExpressionWrapper(F("price") * F("quantity"), output_field=DecimalField())
    )
    total_amount = sales.aggregate(total=Sum("total_price"))["total"] or 0

    template = get_template("sales_report_pdf.html")
    html = template.render({"sales": sales, "total_amount": total_amount})

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response, encoding="UTF-8")

    if pisa_status.err:
        return HttpResponse("PDF generation error <pre>" + html + "</pre>")
    return response


# --------------------------
# Add sale (for testing only)
# --------------------------
@login_required
def add_sale(request):
    if request.method == "POST":
        category = request.POST.get("category")
        item = request.POST.get("item")
        quantity = request.POST.get("quantity")

        # ✅ Secure price
        price = PRICE_LIST.get(item)

        if category and item and quantity and price:
            Sale.objects.create(
                user=request.user,
                category=category,
                item=item,
                quantity=int(quantity),
                price=price,
            )
            return redirect("user_dashboard")

    return render(request, "add_sale.html", {"PRICE_LIST": PRICE_LIST})

