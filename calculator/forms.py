from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Printer, Filament, PrintJob

class BootstrapStyleMixin:
    """Вспомогательный класс для автоматического добавления Bootstrap стилей ко всем полям"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

class PrinterForm(BootstrapStyleMixin, forms.ModelForm):
    class Meta:
        model = Printer
        fields = ['name', 'power_consumption_watts', 'purchase_price', 'estimated_lifespan_hours']


class FilamentForm(BootstrapStyleMixin, forms.ModelForm):
    class Meta:
        model = Filament
        fields = ['brand', 'material_type', 'color', 'purchase_price', 'total_weight_g', 'remaining_weight_g']


class PrintJobForm(BootstrapStyleMixin, forms.ModelForm):
    class Meta:
        model = PrintJob
        fields = ['printer', 'filament', 'model_name', 'print_time_hours', 'sliced_weight_g', 'electricity_rate_kwh', 'is_success']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['printer'].queryset = Printer.objects.filter(user=user)
            self.fields['filament'].queryset = Filament.objects.filter(user=user)


class UserRegisterForm(BootstrapStyleMixin, UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)