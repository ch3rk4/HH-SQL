"""
Модуль для функциональности пользовательского интерфейса.
Предоставляет интерфейс командной строки для взаимодействия с приложением.
"""

from typing import Any, Dict, List

from src.db_manager import DBManager


def display_companies_and_vacancies(data: List[Dict[str, Any]]) -> None:
    """
    Отображение списка компаний и количества их вакансий.
    """
    if not data:
        print("Нет данных о компаниях")
        return

    print("\n=== Компании и количество вакансий ===")
    for item in data:
        print(f"{item['company_name']}: {item['vacancy_count']} вакансий")


def display_all_vacancies(data: List[Dict[str, Any]]) -> None:
    """
    Отображение всех вакансий с их деталями.
    """
    if not data:
        print("Нет данных о вакансиях")
        return

    print("\n=== Все вакансии ===")
    for item in data:
        print(f"Компания: {item['company_name']}")
        print(f"Вакансия: {item['vacancy_name']}")
        print(f"Зарплата: {item['salary']}")
        print(f"URL: {item['url']}")
        print("-" * 50)


def display_avg_salary(data: Dict[str, Any]) -> None:
    """
    Отображение информации о средней зарплате.
    """
    print("\n=== Средняя зарплата ===")
    if data.get("avg_min_salary"):
        print(f"Средняя минимальная зарплата: {data['avg_min_salary']} ₽")
    if data.get("avg_max_salary"):
        print(f"Средняя максимальная зарплата: {data['avg_max_salary']} ₽")
    if data.get("avg_overall"):
        print(f"Средняя зарплата по всем вакансиям: {data['avg_overall']} ₽")


def display_higher_salary_vacancies(data: List[Dict[str, Any]]) -> None:
    """
    Отображение вакансий с зарплатой выше средней.
    """
    if not data:
        print("Нет вакансий с зарплатой выше средней")
        return

    print(f"\n=== Вакансии с зарплатой выше средней ({len(data)} шт.) ===")
    for item in data:
        print(f"Компания: {item['company_name']}")
        print(f"Вакансия: {item['vacancy_name']}")
        print(f"Зарплата: {item['salary']}")
        print(f"URL: {item['url']}")
        print("-" * 50)


def display_keyword_vacancies(data: List[Dict[str, Any]], keyword: str) -> None:
    """
    Отображение вакансий, содержащих указанное ключевое слово.
    """
    if not data:
        print(f"Нет вакансий, содержащих '{keyword}' в названии")
        return

    print(f"\n=== Вакансии, содержащие '{keyword}' ({len(data)} шт.) ===")
    for item in data:
        print(f"Компания: {item['company_name']}")
        print(f"Вакансия: {item['vacancy_name']}")
        print(f"Зарплата: {item['salary']}")
        print(f"URL: {item['url']}")
        print("-" * 50)


def run_user_interface() -> None:
    """
    Запуск пользовательского интерфейса для взаимодействия с приложением.
    """
    db_manager = DBManager()

    while True:
        print("\n=== Меню ===")
        print("1. Показать список компаний и количество вакансий")
        print("2. Показать все вакансии")
        print("3. Показать среднюю зарплату")
        print("4. Показать вакансии с зарплатой выше средней")
        print("5. Поиск вакансий по ключевому слову")
        print("0. Выход")

        choice = input("\nВыберите пункт меню: ")

        if choice == "1":
            data = db_manager.get_companies_and_vacancies_count()
            display_companies_and_vacancies(data)

        elif choice == "2":
            data = db_manager.get_all_vacancies()
            display_all_vacancies(data)

        elif choice == "3":
            data = db_manager.get_avg_salary()
            display_avg_salary(data)

        elif choice == "4":
            data = db_manager.get_vacancies_with_higher_salary()
            display_higher_salary_vacancies(data)

        elif choice == "5":
            keyword = input("Введите ключевое слово для поиска: ")
            data = db_manager.get_vacancies_with_keyword(keyword)
            display_keyword_vacancies(data, keyword)

        elif choice == "0":
            print("До свидания!")
            break

        else:
            print("Неверный выбор. Пожалуйста, выберите пункт из меню.")
