"""
Основная точка входа в приложение.
Обрабатывает инициализацию, получение данных и пользовательский интерфейс.
"""

import time

from src.api import HeadHunterAPI, extract_company_data, extract_vacancy_data
from src.config import COMPANY_IDS
from src.database import (create_database, create_tables, save_employers_to_db,
                          save_vacancies_to_db)
from src.interface import run_user_interface


def init_database() -> None:
    """
    Инициализация базы данных и таблиц.
    """
    print("Инициализация базы данных...")
    create_database()
    create_tables()


def fetch_and_save_data() -> None:
    """
    Получение данных через API и сохранение их в базу данных.
    """
    print("\nПолучение данных из API HeadHunter...")
    api = HeadHunterAPI()

    company_data = api.get_companies_and_vacancies(COMPANY_IDS)

    employers = []
    vacancies = []

    for company_id, data in company_data.items():
        company_info = data.get("company", {})
        company_vacancies = data.get("vacancies", [])

        employer = extract_company_data(company_info)
        employers.append(employer)

        for vacancy in company_vacancies:
            vacancy_data = extract_vacancy_data(vacancy)
            vacancy_data["employer_id"] = company_id
            vacancies.append(vacancy_data)

    print("\nСохранение данных в базу данных...")
    save_employers_to_db(employers)
    save_vacancies_to_db(vacancies)

    print(
        f"\nДанные сохранены: {len(employers)} работодателей и {len(vacancies)} вакансий"
    )


def main() -> None:
    """
    Основная функция для запуска приложения.
    """
    print("=== База данных вакансий HeadHunter ===")

    init_database()

    fetch_and_save_data()

    print("\nБаза данных инициализирована и заполнена данными.")
    time.sleep(1)

    run_user_interface()


if __name__ == "__main__":
    main()
