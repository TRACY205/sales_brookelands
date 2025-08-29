# myapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Sale

# Landing page
def landing(request):
    return render(request, "landing.html")


# User registration
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


# User login
from django.shortcuts import redirect
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff:   # 👈 check if admin/staff
                return redirect("admin_dashboard")
            else:
                return redirect("user_dashboard")
        else:
            return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")


# User logout
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("landing")


# User dashboard
@login_required
def user_dashboard(request):
    if request.method == "POST":
        category = request.POST.get("category")
        item = request.POST.get("item")
        quantity = request.POST.get("quantity")
        price = request.POST.get("price")

        # Basic validation
        if category and item and quantity and price:
            Sale.objects.create(
                user=request.user,
                category=category,
                item=item,
                quantity=int(quantity),
                price=float(price)
            )
            messages.success(request, "Order submitted successfully!")
            return redirect("user_dashboard")
        else:
            messages.error(request, "Please fill all fields correctly.")

    # Get all orders for the logged-in user
    sales = Sale.objects.filter(user=request.user).order_by("-date")
    return render(request, "user_dashboard.html", {"sales": sales})
from django.contrib.admin.views.decorators import staff_member_required

from django.db.models import Sum
from .models import Sale

def admin_dashboard(request):
    sales = Sale.objects.all().order_by("-date")
    total_amount = sales.aggregate(total=Sum("price"))["total"] or 0

    context = {
        "sales": sales,
        "total_amount": total_amount,
    }
    return render(request, "admin_dashboard.html", context)


# views.py
import io
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Sale
from django.db.models import Sum, F, ExpressionWrapper, DecimalField

def admin_dashboard_pdf(request):
    sales = Sale.objects.all()
    total_amount = sales.aggregate(total=Sum("price"))["total"] or 0

    template = get_template("sales_report_pdf.html")
    html = template.render({"sales": sales, "total_amount": total_amount})

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'

    pisa_status = pisa.CreatePDF(io.BytesIO(html.encode("UTF-8")), dest=response, encoding="UTF-8")

    if pisa_status.err:
        return HttpResponse("PDF generation error <pre>" + html + "</pre>")
    return response





def add_sale(request):
    if request.method == "POST":
        category = request.POST.get("category")
        item = request.POST.get("item")
        quantity = request.POST.get("quantity")
        price = request.POST.get("price")

        Sale.objects.create(
            user=request.user,   # 🔑 attach user here
            category=category,
            item=item,
            quantity=quantity,
            price=price,
        )
        return redirect("user_dashboard")

    return render(request, "add_sale.html")
