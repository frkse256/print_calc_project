from django.contrib import admin
from .models import Printer, Filament, PrintJob

@admin.register(Printer)
class PrinterAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'power_consumption_watts', 'total_hours_printed')
    search_fields = ('name', 'user__username')
    list_filter = ('user',)

@admin.register(Filament)
class FilamentAdmin(admin.ModelAdmin):
    list_display = ('brand', 'material_type', 'color', 'remaining_weight_g', 'user')
    search_fields = ('brand', 'material_type', 'color', 'user__username')
    list_filter = ('material_type', 'user')

@admin.register(PrintJob)
class PrintJobAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'printer', 'filament', 'total_cost', 'is_success', 'created_at', 'user')
    search_fields = ('model_name', 'user__username')
    list_filter = ('is_success', 'created_at', 'user')