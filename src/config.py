"""
Конфигурационный модуль для проекта.
Содержит настройки для подключения к базе данных и параметры API.
"""
from typing import Dict, List

# Настройки базы данных
DB_NAME = "headhunter_vacancies"
DB_USER = "postgres"
DB_PASSWORD = "your_password"
DB_HOST = "localhost"
DB_PORT = "5432"

# Настройки API HeadHunter
HH_API_BASE_URL = "https://api.hh.ru"

# Список ID компаний для получения вакансий
# Это примеры ID, их нужно заменить на реальные ID компаний с hh.ru
COMPANY_IDS: List[str] = [
    "1740",    # Яндекс
    "2180",    # Сбербанк
    "2324",    # VK
    "64174",   # Лаборатория Касперского
    "15478",   # Авито
    "239363",  # Тинькофф
    "1122462", # Wildberries
    "2748",    # Ozon
    "1122575", # Skillfactory
    "87021"    # Skyeng
]

# Заголовки запросов к API
API_HEADERS: Dict[str, str] = {
    "User-Agent": "ProjectForEducation/1.0 (your_email@example.com)"
}