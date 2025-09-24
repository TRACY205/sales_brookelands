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
    path("dashboard/", views.user_dashboard, name="user_dashboard"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    # Expenses
    path("add-expense/", views.add_expense, name="add_expense"),          # for adding new expense
    path("upload-expense/", views.upload_expense, name="upload_expense"), # for uploading via Excel
    path("admin-dashboard/expenses-excel/", views.admin_expenses_excel, name="admin_expenses_excel"), # export

    # Sales
    path("add-sale/", views.add_sale, name="add_sale"),                   # for adding new sale
    path("admin-sales-excel/", views.admin_sales_excel, name="admin_sales_excel"),

  
     path("orders/<int:pk>/edit/", views.edit_order, name="edit_order"),
     path("dashboard/", views.user_dashboard, name="dashboard"),
       path("expenses/", views.expenses_list, name="expenses_list"),
    path("expenses/<int:pk>/edit/", views.edit_expense, name="edit_expense"),
      path("edit-sale/<int:sale_id>/", views.edit_sale, name="edit_sale"),
       path("delete-orders/", views.delete_orders, name="delete_orders"), 
        path("delete-sales/", views.delete_sales, name="delete_sales"),
        path("delete-expenses/", views.delete_expenses, name="delete_expenses"),
        path("sales-report/", views.sales_report, name="sales_report"),
path("sales-excel/", views.admin_sales_excel, name="admin_sales_excel"),




]
