"""
Конфигурационный модуль для проекта.
Содержит настройки для подключения к базе данных и параметры API.
Загружает конфиденциальные данные из .env-файла.
"""
import os
from typing import Dict, List
from dotenv import load_dotenv

# Загрузка переменных из .env-файла
load_dotenv()

# Настройки базы данных
DB_NAME = os.getenv("DB_NAME", "headhunter_vacancies")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Настройки API HeadHunter
HH_API_BASE_URL = "https://api.hh.ru"
HH_API_USER_AGENT = os.getenv("HH_API_USER_AGENT", "ProjectForEducation/1.0")
HH_API_EMAIL = os.getenv("HH_API_EMAIL", "your_email@example.com")

# Список ID компаний для получения вакансий
COMPANY_IDS: List[str] = [
    "1740",    # Яндекс
    "3529",    # Сбербанк
    "15478",   # VK
    "1057",    # Лаборатория Касперского
    "84585",   # Авито
    "78638",   # Тинькофф
    "87021",   # Wildberries
    "2180",    # Ozon
    "3305437", # Gear Games
    "1122462"  # Skyeng
]

# Заголовки запросов к API
API_HEADERS: Dict[str, str] = {
    "User-Agent": f"{HH_API_USER_AGENT} ({HH_API_EMAIL})"
}