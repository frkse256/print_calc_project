import decimal
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Printer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='printers')
    name = models.CharField(max_length=100, verbose_name="Модель принтера")
    power_consumption_watts = models.PositiveIntegerField(default=350, verbose_name="Энергопотребление (Вт)")
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость принтера (руб)")
    estimated_lifespan_hours = models.PositiveIntegerField(default=2000, verbose_name="Ресурс до ТО/замены (часов)")
    total_hours_printed = models.FloatField(default=0.0, verbose_name="Всего отработано часов")

    def __str__(self):
        return f"{self.name} ({self.total_hours_printed:.1f} ч)"


class Filament(models.Model):
    MATERIAL_CHOICES = [
        ('PLA', 'PLA'),
        ('PETG', 'PETG'),
        ('ABS', 'ABS'),
        ('TPU', 'TPU/Flex'),
        ('NYLON', 'Nylon'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='filaments')
    brand = models.CharField(max_length=100, verbose_name="Производитель")
    material_type = models.CharField(max_length=10, choices=MATERIAL_CHOICES, verbose_name="Тип пластика")
    color = models.CharField(max_length=50, verbose_name="Цвет")
    purchase_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена за катушку (руб)")
    total_weight_g = models.PositiveIntegerField(default=1000, verbose_name="Вес катушки (грамм)")
    remaining_weight_g = models.PositiveIntegerField(default=1000, verbose_name="Остаток пластика (грамм)")

    def __str__(self):
        return f"{self.brand} {self.material_type} ({self.color}) — {self.remaining_weight_g}г"


class PrintJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='print_jobs')
    printer = models.ForeignKey(Printer, on_delete=models.CASCADE, related_name='jobs', verbose_name="Принтер")
    filament = models.ForeignKey(Filament, on_delete=models.CASCADE, related_name='jobs', verbose_name="Пластик")
    model_name = models.CharField(max_length=200, verbose_name="Название модели")

    print_time_hours = models.FloatField(verbose_name="Время печати (часов)")
    sliced_weight_g = models.PositiveIntegerField(verbose_name="Вес по слайсеру (грамм)")
    electricity_rate_kwh = models.DecimalField(max_digits=5, decimal_places=2, default=5.50,
                                               verbose_name="Тариф за кВтч (руб)")
    is_success = models.BooleanField(default=True, verbose_name="Успешная печать")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    plastic_cost = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True,
                                       verbose_name="Стоимость пластика")
    electricity_cost = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True,
                                           verbose_name="Стоимость электричества")
    wear_cost = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True,
                                    verbose_name="Стоимость износа")
    total_cost = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True,
                                     verbose_name="Итоговая себестоимость")

    def calculate_costs(self):
        price_per_gram = self.filament.purchase_price / self.filament.total_weight_g
        self.plastic_cost = price_per_gram * self.sliced_weight_g

        power_kw = decimal.Decimal(self.printer.power_consumption_watts) / 1000
        hours_dec = decimal.Decimal(self.print_time_hours)
        kwh_used = power_kw * hours_dec
        self.electricity_cost = kwh_used * self.electricity_rate_kwh

        hourly_amortization = self.printer.purchase_price / decimal.Decimal(self.printer.estimated_lifespan_hours)
        self.wear_cost = hourly_amortization * hours_dec

        self.total_cost = self.plastic_cost + self.electricity_cost + self.wear_cost

    def clean(self):
        if self.sliced_weight_g > self.filament.remaining_weight_g:
            raise ValidationError(
                f"Недостаточно пластика! На катушке осталось только {self.filament.remaining_weight_g}г.")

    def save(self, *args, **kwargs):
        self.calculate_costs()

        if not self.pk:
            self.clean()
            # Уменьшаем вес пластика в БД
            self.filament.remaining_weight_g = models.F('remaining_weight_g') - self.sliced_weight_g
            self.filament.save()

            # Увеличиваем наработку принтера
            self.printer.total_hours_printed = models.F('total_hours_printed') + self.print_time_hours
            self.printer.save()

        super().save(*args, **kwargs)