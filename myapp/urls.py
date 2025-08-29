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
    path("dashboard/", views.user_dashboard, name="user_dashboard"),                # User dashboard
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),        # Admin dashboard
  path("admin-dashboard/pdf/", views.admin_dashboard_pdf, name="admin_dashboard_pdf"),
  path("add-sale/", views.add_sale, name="add_sale"), 

]
 

