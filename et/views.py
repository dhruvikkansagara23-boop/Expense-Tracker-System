


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from .models import Expense,  Category
import json
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from .validator.email_validator import validate_email_format
from .validator.password_validator import validate_strong_password


User = get_user_model()

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm-password', '')
        force = request.POST.get('force', '')

    
        if not email or not password:
            return render(request, 'et/signup.html', {'error': 'Email and password required.'})

        if password != confirm:
            return render(request, 'et/signup.html', {'error': 'Passwords do not match.'})

        if User.objects.filter(email=email).exists():
            return render(request, 'et/signup.html', {'error': 'Email already exists.'})

        if not validate_email_format(email):
            return render(request, 'et/signup.html', {'error': 'Invalid email format.'})

        if not validate_strong_password(password) and not force:
            return render(request, 'et/signup.html', {
                'password_msg': 'Weak password — must include uppercase, lowercase, number, and special character.',
                'weak_password': True,
                'email': email,
                'password': password,
                'confirm': confirm
            })

        user = User.objects.create_user(username=email, email=email, password=password)
        messages.success(request, 'Account created successfully! Please log in.')
        return redirect('et:login')

    return render(request, 'et/signup.html')





def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return redirect('et:dashboard')
        else:
            return render(request, 'et/login.html', {'error': 'Invalid credentials.'})
    return render(request, 'et/login.html')


def logout_view(request):
    logout(request)
    return redirect('et:login')



from django.db.models.functions import TruncMonth
from .models import  Expense


@login_required
def dashboard_view(request):
    user = request.user
    expenses = Expense.objects.filter(user=user).order_by('-date')

    month = request.GET.get('month')
    if month:
        try:
            year, mon = map(int, month.split('-'))
            expenses = expenses.filter(date__year=year, date__month=mon)
          
        except Exception:
            pass

    total_expense = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    balance =  total_expense

 
    cat_qs = Expense.objects.filter(user=user).values('category__name').annotate(total=Sum('amount'))
    cat_labels = [c['category__name'] or 'Uncategorized' for c in cat_qs]
    cat_data = [float(c['total']) if c['total'] is not None else 0.0 for c in cat_qs]
    
 
    all_months = set(Expense.objects.filter(user=user).annotate(month=TruncMonth('date')).values_list('month', flat=True))
    

    sorted_months = sorted(list(all_months))
    line_labels = [m.strftime('%Y-%m') for m in sorted_months]
 
    expense_agg = {x['month']: x['total'] for x in Expense.objects.filter(user=user).annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount'))}

    line_expense_data = [float(expense_agg.get(m, Decimal('0.00'))) for m in sorted_months]

 
    
    context = {
        'expenses': expenses,
        'total': total_expense,
        'balance': balance,
        
  
        'cat_labels': json.dumps(cat_labels),
        'cat_data': json.dumps(cat_data),
        
    
        'line_labels': json.dumps(line_labels),
        'line_expense_data': json.dumps(line_expense_data),
    }
    
    
    return render(request, 'et/dashboard.html', context)
 


@login_required
def add_expense(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        amount = request.POST.get('amount')
        date = request.POST.get('date')
        description = request.POST.get('description', '')
        category_id = request.POST.get('category')
        category = None
        if category_id:
            try:
                category = Category.objects.get(id=int(category_id), user=request.user)
            except Exception:
                category = None

        if not (title and amount and date):
            return render(request, 'et/add_expense.html', {'error': 'All required fields missing.', 'categories': Category.objects.filter(user=request.user)})

        Expense.objects.create(
            user=request.user,
            title=title,
            amount=amount,
            date=date,
            description=description,
            category=category
        )
        return redirect('et:dashboard')

    categories = Category.objects.filter(user=request.user)
    return render(request, 'et/add_expense.html', {'categories': categories})


@login_required
def edit_expense(request, id):
    expense = get_object_or_404(Expense, id=id, user=request.user)
    if request.method == 'POST':
        expense.title = request.POST.get('title', expense.title)
        expense.amount = request.POST.get('amount', expense.amount)
        expense.date = request.POST.get('date', expense.date)
        expense.description = request.POST.get('description', expense.description)
        category_id = request.POST.get('category')
        if category_id:
            try:
                expense.category = Category.objects.get(id=int(category_id), user=request.user)
            except Exception:
                expense.category = None
        expense.save()
        return redirect('et:dashboard')
    categories = Category.objects.filter(user=request.user)
    return render(request, 'et/edit_expense.html', {'expense': expense, 'categories': categories})


@login_required
def delete_expense(request, id):
    exp = get_object_or_404(Expense, id=id, user=request.user)
    exp.delete()
    return redirect('et:dashboard')


@login_required
def categories_view(request):
    cats = Category.objects.all()  
    return render(request, 'et/categories.html', {'categories': cats})


@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            return render(request, 'et/add_category.html', {'error': 'Name required'})
        Category.objects.create(user=request.user, name=name)
        return redirect('et:categories')
    return render(request, 'et/add_category.html')










import csv
import io
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse

from django.contrib import messages

from .models import  Expense



@login_required
def export_expenses_csv(request):
   
    month = request.GET.get('month')
    qs = Expense.objects.filter(user=request.user).order_by('-date')
    if month:
        try:
            year, mon = map(int, month.split('-'))
            qs = qs.filter(date__year=year, date__month=mon)
        except Exception:
            pass

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Title', 'Amount', 'Date', 'Category', 'Description'])
    for e in qs:
        writer.writerow([e.title, str(e.amount), e.date.isoformat(), getattr(e, 'category', None) or '', e.description or ''])
    output.seek(0)
    filename = f"expenses_{request.user.username}_{month or 'all'}.csv"
    resp = HttpResponse(output, content_type='text/csv')
    resp['Content-Disposition'] = f'attachment; filename="{filename}"'
    return resp


@login_required
def export_expenses_pdf(request):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception:
        messages.error(request, "ReportLab not installed. Install with: pip install reportlab")
        return redirect('et:dashboard')

    month = request.GET.get('month')
    qs = Expense.objects.filter(user=request.user).order_by('-date')
    if month:
        try:
            year, mon = map(int, month.split('-'))
            qs = qs.filter(date__year=year, date__month=mon)
        except Exception:
            pass

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    x, y = 40, 750
    c.setFont("Helvetica-Bold", 14)
    title = f"Expenses Report - {request.user.username} - {month or 'All'}"
    c.drawString(x, y, title)
    y -= 30
    c.setFont("Helvetica", 10)
    for e in qs:
        line = f"{e.date} | {e.title} | Rs.{e.amount} | {getattr(e, 'category', '')}"
        c.drawString(x, y, line)
        y -= 14
        if y < 60:
            c.showPage()
            y = 750
    c.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f"expenses_{request.user.username}_{month or 'all'}.pdf")

