"""
Модуль для взаимодействия с API HeadHunter.
Предоставляет классы и функции для получения данных о работодателях и вакансиях.
"""

import time
from typing import Any, Dict, List, Optional, Union

import requests

from src.config import API_HEADERS, COMPANY_IDS, HH_API_BASE_URL


class HeadHunterAPI:
    """
    Класс для взаимодействия с API HeadHunter.
    """

    def __init__(
        self, base_url: str = HH_API_BASE_URL, headers: Dict[str, str] = API_HEADERS
    ):
        """
        Инициализация класса HeadHunterAPI с базовым URL и заголовками.
        """
        self.base_url = base_url
        self.headers = headers

    def _make_request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Выполнение запроса к API HeadHunter.
        """
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 429:
            time.sleep(2)
            return self._make_request(endpoint, params)

        response.raise_for_status()

        return response.json()

    def get_employer(self, employer_id: str) -> Dict[str, Any]:
        """
        Получение информации о конкретном работодателе по ID.
        """
        endpoint = f"employers/{employer_id}"
        return self._make_request(endpoint)

    def get_employer_vacancies(
        self, employer_id: str, page: int = 0, per_page: int = 100
    ) -> Dict[str, Any]:
        """
        Получение вакансий для конкретного работодателя.
        """
        endpoint = "vacancies"
        params = {"employer_id": employer_id, "page": page, "per_page": per_page}
        return self._make_request(endpoint, params)

    def get_all_employer_vacancies(self, employer_id: str) -> List[Dict[str, Any]]:
        """
        Получение всех вакансий для конкретного работодателя с обработкой пагинации.
        """
        all_vacancies = []
        page = 0
        per_page = 100

        while True:
            response = self.get_employer_vacancies(employer_id, page, per_page)
            vacancies = response.get("items", [])
            all_vacancies.extend(vacancies)

            if page >= response.get("pages", 0) - 1 or not vacancies:
                break

            page += 1
            time.sleep(0.2)

        return all_vacancies

    def get_companies_and_vacancies(
        self, company_ids: List[str] = COMPANY_IDS
    ) -> Dict[str, Dict[str, Union[Dict[str, Any], List[Dict[str, Any]]]]]:
        """
        Получение информации о нескольких компаниях и их вакансиях.
        """
        result = {}

        for company_id in company_ids:
            try:
                company_info = self.get_employer(company_id)

                vacancies = self.get_all_employer_vacancies(company_id)

                result[company_id] = {"company": company_info, "vacancies": vacancies}

                time.sleep(0.5)

                print(
                    f"Получены данные для компании {company_info.get('name', company_id)}: {len(vacancies)} вакансий"
                )
            except Exception as e:
                print(
                    f"Ошибка при получении данных для компании {company_id}: {str(e)}"
                )

        return result


def normalize_salary(salary_data: Optional[Dict[str, Any]]) -> Dict[str, Optional[int]]:
    """
    Нормализация данных о зарплате из API HeadHunter.
    """
    if not salary_data:
        return {"min_salary": None, "max_salary": None, "currency": None}

    min_salary = salary_data.get("from")
    max_salary = salary_data.get("to")
    currency = salary_data.get("currency")

    # Конвертация в рубли при необходимости
    if currency and currency.lower() != "rub":
        conversion_rates = {"usd": 75, "eur": 85}
        rate = conversion_rates.get(currency.lower(), 1)

        if min_salary:
            min_salary = min_salary * rate

        if max_salary:
            max_salary = max_salary * rate

        currency = "RUB"

    return {"min_salary": min_salary, "max_salary": max_salary, "currency": currency}


def extract_vacancy_data(vacancy: Dict[str, Any]) -> Dict[str, Any]:
    """
    Извлечение релевантных данных из словаря вакансии.
    """
    normalized_salary = normalize_salary(vacancy.get("salary"))

    return {
        "id": vacancy.get("id"),
        "name": vacancy.get("name"),
        "area": vacancy.get("area", {}).get("name") if vacancy.get("area") else None,
        "url": vacancy.get("alternate_url"),
        "min_salary": normalized_salary["min_salary"],
        "max_salary": normalized_salary["max_salary"],
        "currency": normalized_salary["currency"],
        "published_at": vacancy.get("published_at"),
        "requirement": (
            vacancy.get("snippet", {}).get("requirement")
            if vacancy.get("snippet")
            else None
        ),
        "responsibility": (
            vacancy.get("snippet", {}).get("responsibility")
            if vacancy.get("snippet")
            else None
        ),
    }


def extract_company_data(company: Dict[str, Any]) -> Dict[str, Any]:
    """
    Извлечение релевантных данных из словаря компании.
    """
    return {
        "id": company.get("id"),
        "name": company.get("name"),
        "url": company.get("alternate_url"),
        "description": company.get("description"),
        "area": company.get("area", {}).get("name") if company.get("area") else None,
        "site_url": company.get("site_url"),
        "industry": (
            company.get("industries", [{}])[0].get("name")
            if company.get("industries")
            else None
        ),
    }
