from django.contrib import admin
from .models import Printer, Filament, PrintJob

admin.site.register(Printer)
admin.site.register(Filament)
admin.site.register(PrintJob)