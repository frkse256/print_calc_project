from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Printer, Filament, PrintJob


class PrintCalculatorTestCase(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Создаем тестовый принтер
        self.printer = Printer.objects.create(
            user=self.user,
            name="Prusa i3",
            power_consumption_watts=300,
            purchase_price=50000.00,
            estimated_lifespan_hours=2000
        )

        # Создаем тестовую катушку пластика
        self.filament = Filament.objects.create(
            user=self.user,
            brand="BestFil",
            material_type="PLA",
            color="Black",
            purchase_price=2000.00,
            total_weight_g=1000,
            remaining_weight_g=1000
        )

    def test_printer_creation(self):
        """Проверка корректности создания принтера"""
        self.assertEqual(self.printer.name, "Prusa i3")
        self.assertEqual(self.printer.total_hours_printed, 0.0)

    def test_filament_creation(self):
        """Проверка создания катушки и начального остатка"""
        self.assertEqual(self.filament.brand, "BestFil")
        self.assertEqual(self.filament.remaining_weight_g, 1000)

    def test_cost_calculation_math(self):
        """Проверка математических расчетов себестоимости по формулам"""
        job = PrintJob(
            user=self.user,
            printer=self.printer,
            filament=self.filament,
            model_name="Benchy",
            print_time_hours=2.0,
            sliced_weight_g=15,
            electricity_rate_kwh=5.00
        )
        job.calculate_costs()

        # 1. Расчет пластика: (2000 руб / 1000г) * 15г = 30.00 руб
        self.assertEqual(float(job.plastic_cost), 30.00)

        # 2. Расчет энергии: (300 Вт / 1000) * 2.0 ч * 5.00 руб = 3.00 руб
        self.assertEqual(float(job.electricity_cost), 3.00)

        # 3. Расчет амортизации: (50000 руб / 2000 ч) * 2.0 ч = 50.00 руб
        self.assertEqual(float(job.wear_cost), 50.00)

        # 4. Итоговая сумма: 30 + 3 + 50 = 83.00 руб
        self.assertEqual(float(job.total_cost), 83.00)

    def test_materials_deduction_on_save(self):
        """Проверка автоматического списания веса и начисления пробега при сохранении"""
        PrintJob.objects.create(
            user=self.user,
            printer=self.printer,
            filament=self.filament,
            model_name="Test Model",
            print_time_hours=1.5,
            sliced_weight_g=100,
            electricity_rate_kwh=5.00
        )

        # Перезагружаем объекты из базы данных
        self.filament.refresh_from_db()
        self.printer.refresh_from_db()

        # Было 1000г, списали 100г -> должно остаться 900г
        self.assertEqual(self.filament.remaining_weight_g, 900)
        # Было 0ч работы принтера, печатали 1.5ч -> пробег должен стать 1.5ч
        self.assertEqual(self.printer.total_hours_printed, 1.5)

    def test_insufficient_filament_validation(self):
        """Проверка защиты: нельзя напечатать деталь тяжелее остатка катушки"""
        job = PrintJob(
            user=self.user,
            printer=self.printer,
            filament=self.filament,
            model_name="Huge Model",
            print_time_hours=10.0,
            sliced_weight_g=1200,  # Запрошено больше, чем 1000г на катушке
            electricity_rate_kwh=5.00
        )
        # Ожидаем вызов ошибки валидации при проверке модели
        with self.assertRaises(ValidationError):
            job.full_clean()