
from django.shortcuts import redirect
from django.urls import path
from . import views

app_name = 'et'

urlpatterns = [
    
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('edit_expense/<int:expense_id>/', views.edit_expense, name='edit_expense'),
    path('delete_expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('categories/', views.categories_view, name='categories'),
    path('add_category/', views.add_category, name='add_category'),
    path('export_expenses_csv/', views.export_expenses_csv, name='export_expenses_csv'),
    path('export_expenses_pdf/', views.export_expenses_pdf, name='export_expenses_pdf'),
]
