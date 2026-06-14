import pandas as pd
import plotly.express as px
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Printer, Filament, PrintJob
from .forms import PrinterForm, FilamentForm, PrintJobForm, UserRegisterForm
from django.db.models import Sum

def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Регистрация прошла успешно. Войдите в систему.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})


# --- Управление принтерами ---
@login_required
def printer_list(request):
    printers = Printer.objects.filter(user=request.user)
    return render(request, 'printer_list.html', {'printers': printers})


@login_required
def printer_create(request):
    if request.method == 'POST':
        form = PrinterForm(request.POST)
        if form.is_valid():
            printer = form.save(commit=False)
            printer.user = request.user
            printer.save()
            return redirect('printer_list')
    else:
        form = PrinterForm()
    return render(request, 'printer_form.html', {'form': form, 'title': 'Добавить принтер'})


# --- Управление катушками пластика ---
@login_required
def filament_list(request):
    filaments = Filament.objects.filter(user=request.user)
    return render(request, 'filament_list.html', {'filaments': filaments})


@login_required
def filament_create(request):
    if request.method == 'POST':
        form = FilamentForm(request.POST)
        if form.is_valid():
            filament = form.save(commit=False)
            filament.user = request.user
            filament.save()
            return redirect('filament_list')
    else:
        form = FilamentForm()
    return render(request, 'filament_form.html', {'form': form, 'title': 'Добавить пластик'})


# --- Управление заданиями печати ---
@login_required
def job_list(request):
    jobs = PrintJob.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'job_list.html', {'jobs': jobs})


@login_required
def job_create(request):
    if request.method == 'POST':
        form = PrintJobForm(request.POST, user=request.user)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            try:
                job.save()
                return redirect('job_list')
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = PrintJobForm(user=request.user)
    return render(request, 'job_form.html', {'form': form})


# --- Аналитический модуль (Pandas + Plotly) ---
@login_required
def analytics(request):
    jobs_queryset = PrintJob.objects.filter(user=request.user).values(
        'created_at', 'plastic_cost', 'electricity_cost', 'wear_cost', 'total_cost', 'is_success'
    )

    if not jobs_queryset.exists():
        return render(request, 'analytics.html', {'no_data': True})

    # Обработка данных через Pandas
    df = pd.DataFrame(list(jobs_queryset))

    # Преобразование типов для исключения проблем при сериализации в графиках
    for col in ['plastic_cost', 'electricity_cost', 'wear_cost', 'total_cost']:
        df[col] = df[col].astype(float)

    # Основные метрики
    total_spend = df['total_cost'].sum()
    success_rate = (df['is_success'].sum() / len(df)) * 100
    total_hours = PrintJob.objects.filter(user=request.user).aggregate(Sum('print_time_hours'))['print_time_hours__sum'] or 0

    # Группировка структуры затрат
    cost_structure = {
        'Категория': ['Пластик', 'Электричество', 'Износ оборудования'],
        'Сумма (руб)': [
            df['plastic_cost'].sum(),
            df['electricity_cost'].sum(),
            df['wear_cost'].sum()
        ]
    }
    df_structure = pd.DataFrame(cost_structure)

    # Построение круговой диаграммы через Plotly
    fig_pie = px.pie(
        df_structure,
        values='Сумма (руб)',
        names='Категория',
        title='Распределение затрат в бюджете',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_pie.update_layout(margin=dict(t=50, b=20, l=20, r=20))
    chart_div = fig_pie.to_html(full_html=False)

    context = {
        'total_spend': round(total_spend, 2),
        'success_rate': round(success_rate, 1),
        'total_hours': round(total_hours, 1),
        'total_jobs_count': len(df),
        'chart_div': chart_div,
    }

    return render(request, 'analytics.html', context)