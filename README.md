# Проект HeadHunter Vacancies Database

Проект для сбора и анализа вакансий с сайта [HeadHunter](https://hh.ru). Приложение получает данные о компаниях и их вакансиях через API HeadHunter, сохраняет информацию в базу данных PostgreSQL и предоставляет интерфейс для работы с полученными данными.

## Возможности

- Получение данных о компаниях и вакансиях через API HeadHunter
- Сохранение данных в базу данных PostgreSQL
- Фильтрация вакансий по различным параметрам
- Анализ зарплатных предложений
- Поиск вакансий по ключевым словам
- Получение статистики по компаниям

## Структура проекта

```
project_root/
├── src/
│   ├── __init__.py
│   ├── api.py         # Модуль для работы с API HeadHunter
│   ├── database.py    # Модуль для работы с базой данных
│   ├── db_manager.py  # Класс для управления данными в БД
│   ├── interface.py   # Пользовательский интерфейс
│   └── config.py      # Конфигурационные параметры
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_database.py
│   ├── test_db_manager.py
│   ├── test_interface.py
│   ├── test_main.py
│   └── test_config.py
├── main.py            # Основной скрипт
├── main_test.py       # Точка входа для запуска всех тестов
├── .env.example       # Пример конфигурации .env файла
├── .gitignore         # Список игнорируемых файлов для Git
└── requirements.txt   # Зависимости проекта
```

## Требования

- Python 3.8+
- PostgreSQL 12+
- Библиотеки из файла requirements.txt

## Установка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/yourusername/headhunter-vacancies-db.git
   cd headhunter-vacancies-db
   ```

2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv venv
   # Для Windows
   venv\Scripts\activate
   # Для Linux/Mac
   source venv/bin/activate
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Создайте и настройте файл .env:
   ```bash
   cp .env.example .env
   ```

5. Настройте параметры подключения к базе данных PostgreSQL в файле .env

## Настройка .env файла

Проект использует .env файл для хранения конфиденциальных данных, таких как параметры подключения к базе данных. Для настройки окружения:

1. Создайте файл `.env` в корневой директории проекта на основе примера `.env.example`:
   ```bash
   cp .env.example .env
   ```

2. Отредактируйте файл `.env`, указав ваши настройки:
   ```
   # База данных
   DB_NAME=headhunter_vacancies
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   
   # API HeadHunter
   HH_API_USER_AGENT=ProjectForEducation/1.0
   HH_API_EMAIL=your_email@example.com
   ```

3. Замените значения в файле на актуальные для вашей системы:
   - `DB_NAME`: Имя базы данных PostgreSQL для сохранения данных
   - `DB_USER`: Имя пользователя PostgreSQL
   - `DB_PASSWORD`: Пароль пользователя PostgreSQL
   - `DB_HOST`: Хост для подключения к PostgreSQL (обычно localhost)
   - `DB_PORT`: Порт для подключения к PostgreSQL (обычно 5432)
   - `HH_API_USER_AGENT`: Идентификатор пользовательского агента для API HeadHunter
   - `HH_API_EMAIL`: Ваш email для API HeadHunter

**Важно:** Файл `.env` добавлен в `.gitignore` и не будет включен в репозиторий, что обеспечивает безопасность ваших данных. Никогда не коммитьте файл с реальными учетными данными в репозиторий.

## Использование

1. Запустите основной скрипт:
   ```bash
   python main.py
   ```

2. После запуска скрипт выполнит следующие операции:
   - Инициализирует базу данных (создаст БД и необходимые таблицы)
   - Получит данные о компаниях и вакансиях через API HeadHunter
   - Сохранит полученные данные в базу данных
   - Запустит интерактивный пользовательский интерфейс

3. Доступные опции в пользовательском интерфейсе:
   - Получить список всех компаний и количество вакансий у каждой компании
   - Получить список всех вакансий с указанием названия компании, названия вакансии и зарплаты
   - Получить среднюю зарплату по вакансиям
   - Получить список вакансий, у которых зарплата выше средней
   - Получить список вакансий, в названии которых содержится ключевое слово

## ID компаний HeadHunter

В проекте используются ID компаний с HeadHunter. Вы можете найти ID интересующих вас компаний одним из следующих способов:

1. Через URL компании на сайте hh.ru:
   - Откройте страницу компании на hh.ru
   - В адресной строке вы увидите URL вида `https://hh.ru/employer/1740`
   - Число в конце URL (например, "1740") - это ID компании

2. Через поиск работодателей на сайте:
   - Перейдите на страницу поиска работодателей: https://hh.ru/employers_list
   - Найдите интересующую компанию
   - Наведите курсор на название компании и посмотрите URL в статусе браузера

3. Через API HeadHunter (пример в коде):
   ```python
   import requests

   def search_companies(company_name):
       url = "https://api.hh.ru/employers"
       params = {
           "text": company_name,
           "per_page": 10
       }
       headers = {
           "User-Agent": "ProjectForEducation/1.0 (your_email@example.com)"
       }
       
       response = requests.get(url, params=params, headers=headers)
       data = response.json()
       
       print(f"Найдено {data['found']} компаний:")
       for company in data['items']:
           print(f"ID: {company['id']}, Название: {company['name']}")
       
       return data['items']

   # Пример использования
   company_name = input("Введите название компании для поиска: ")
   companies = search_companies(company_name)
   ```

В конфигурационном файле (`src/config.py`) вы можете заменить список ID компаний на интересующие вас.

## Тестирование

Для запуска всех тестов выполните:

```bash
python main_test.py
```

Для запуска отдельного тестового модуля:

```bash
python -m unittest tests.test_api
python -m unittest tests.test_database
python -m unittest tests.test_db_manager
# и т.д.
```

## Лицензия

Этот проект распространяется под лицензией MIT. См. файл LICENSE для получения дополнительной информации.