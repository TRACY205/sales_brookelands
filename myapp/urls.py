# myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Landing + Authentication
    path("", views.landing, name="landing"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboards
    path("dashboard/", views.user_dashboard, name="user_dashboard"),       # User dashboard
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),  # Admin dashboard

    # Sales & Expenses
    path("add-sale/", views.add_sale, name="add_sale"),
    path("add-expense/", views.add_expense, name="add_expense"),
    path("upload-expense/", views.upload_expense, name="upload_expense"),

    # PDF Reports
    path("admin-dashboard/pdf/", views.admin_expenses_pdf, name="admin_dashboard_pdf"),
]

