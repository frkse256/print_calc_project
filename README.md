# 3D-Printer Cost & Wear Analyzer

Специализированный веб-сервис для владельцев 3D-принтеров и домашних мастерских, позволяющий рассчитывать точную себестоимость каждого сеанса печати. Система учитывает расходы на пластик, затраченную электроэнергию по локальным тарифам и амортизационный износ оборудования, помогая оптимизировать бюджет мастерской.

**Ссылка на рабочий проект:** [https://freskor.pythonanywhere.com/](https://freskor.pythonanywhere.com/)

## Технологии
* **Python 3.10 / 3.13**
* **Django 4.2**
* **Pandas 2.x** (аналитическая группировка данных)
* **Plotly 5.x** (интерактивные графики структуры затрат)
* **Bootstrap 5** (адаптивная верстка интерфейса)

## Скриншоты интерфейса

![Главная страница](https://raw.githubusercontent.com/frkse256/print_calc_project/main/static/screenshots/main.png)
*Посадочная страница сервиса*

![Аналитический дашборд](https://raw.githubusercontent.com/frkse256/print_calc_project/main/static/screenshots/analytics.png)
*Интерактивная диаграмма распределения бюджета, построенная с помощью Plotly*

![История печати](https://raw.githubusercontent.com/frkse256/print_calc_project/main/static/screenshots/history.png)
*Журнал выполненных запусков с расчетом себестоимости каждой детали*

---

## Как запустить проект локально

1. **Клонируйте репозиторий:**
   ```bash
   git clone https://github.com/ваш-юзернейм/ваш-репо.git
   cd print_calc_project
2. **Создайте и активируйте виртуальное окружение:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Linux/Mac
    venv\Scripts\activate     # Для Windows

3. **Установите все необходимые зависимости:**
    ```bash
    pip install -r requirements.txt

4. **Выполните миграции для создания базы данных SQLite:**
    ```bash
    python manage.py migrate

5. **Создайте учетную запись администратора Django:**
    ```bash
    python manage.py createsuperuser

6. **Запустите локальный сервер разработки:**
    ```bash
    python manage.py runserver

7. **Откройте проект в браузере:**
    Перейдите по ссылке: http://127.0.0.1:8000/

Программный интерфейс (API)

Проект предоставляет собственный API-эндпоинт для интеграции со сторонними системами (например, вашим слайсером или умной розеткой):

    GET /api/printers/ — возвращает список принтеров текущего авторизованного пользователя и их текущую наработку в формате JSON.