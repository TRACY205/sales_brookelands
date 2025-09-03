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
# User dashboard
# --------------------------
# myapp/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Sale

# ✅ Full PRICE LIST including Water and Gas
PRICE_LIST = {
    # Water
    "1L + B": 30,
    "1L (Refill)": 10,
    "5L (Refill)": 70,
    "5L + Bottle": 150,
    "10L (Refill)": 130,
    "10L + Bottle": 250,
    "20L (Refill)": 250,
    "20L + Bottle": 500,
    "20L (Hard) + Water": 1500,

    # Gas
    "Insta Gas 6kg": 1000,
    "Insta Gas 12kg": 3500,
    "Pro Gas 6kg": 1000,
    "Pro Gas 12kg": 3500,
    "Wajiko 6kg": 1000,
    "Wajiko 12kg": 3500,
    "K Gas 6kg": 1000,
    "K Gas 12kg": 3500,
    "Afri Gas 6kg": 1000,
    "Afri Gas 12kg": 3500,
    "Total Gas 6kg": 1000,
    "Total Gas 12kg": 3500,
}

@login_required
def user_dashboard(request):
    if request.method == "POST":
        category = request.POST.get("category")
        item = request.POST.get("item")
        payment_method = request.POST.get("payment_method")

        # Convert quantity safely
        try:
            quantity = int(request.POST.get("quantity"))
        except (TypeError, ValueError):
            quantity = 0

        # Get unit price from full PRICE_LIST
        unit_price = PRICE_LIST.get(item)

        # Validate all fields
        if not category or not item or quantity <= 0 or unit_price is None or not payment_method:
            messages.error(request, "⚠️ Please fill all fields correctly.")
            return redirect("user_dashboard")

        # Calculate total price
        total_price = unit_price * quantity

        # Create Sale
        Sale.objects.create(
            user=request.user,
            category=category,
            item=item,
            quantity=quantity,
            price=total_price,
            payment_method=payment_method
        )

        messages.success(request, "✅ Order submitted successfully!")
        return redirect("user_dashboard")

    # Display all user sales
    sales = Sale.objects.filter(user=request.user).order_by("-date")
    return render(request, "user_dashboard.html", {"sales": sales})


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
    sales = Sale.objects.all()
    total_amount = sum(sale.price * sale.quantity for sale in sales)  # ✅ multiply price by quantity
    template_path = 'admin_dashboard_pdf.html'
    context = {'sales': sales, 'total_amount': total_amount}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="sales_report.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
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
        payment_method = request.POST.get("payment_method")  # ✅ add payment method

        try:
            quantity = int(quantity)
        except:
            quantity = 0

        unit_price = PRICE_LIST.get(item)

        if category and item and quantity > 0 and unit_price is not None and payment_method:
            Sale.objects.create(
                user=request.user,
                category=category,
                item=item,
                quantity=quantity,
                price=unit_price,          # store unit price
                payment_method=payment_method
            )
            return redirect("user_dashboard")

    return render(request, "add_sale.html", {"PRICE_LIST": PRICE_LIST})


