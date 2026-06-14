# 3D-Print Cost & Wear Analyzer

Веб-сервис для автоматизации расчетов себестоимости 3D-печати. Помогает мейкерам вести учет расхода пластика, электроэнергии и амортизации оборудования.

**Ссылка на рабочий проект:** https://freskor.pythonanywhere.com/

## Технологии
* **Python 3.13** (на хостинге рекомендуется Python 3.10)
* **Django 4.2**
* **Pandas** (анализ данных)
* **Plotly** (интерактивные графики)
* **Bootstrap 5** (интерфейс)

## Как запустить проект локально
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/frkse256/print_calc_project

2. Создайте и запустите виртуальное окружение:

    ```bash
    python -m venv venv
    
   venv\Scripts\activate

3. Установите зависимости:
    ```bash
    pip install -r requirements.txt

4. Выполните миграции:
    ```bash
    python manage.py migrate

5. Запустите сервер:
    ```bash
    python manage.py runserver