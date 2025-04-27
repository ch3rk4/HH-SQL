"""
Модуль для тестирования пользовательского интерфейса.
"""

import io
import sys
import unittest
from unittest.mock import MagicMock, call, patch

from src.interface import (display_all_vacancies, display_avg_salary,
                           display_companies_and_vacancies,
                           display_higher_salary_vacancies,
                           display_keyword_vacancies, run_user_interface)


class TestInterface(unittest.TestCase):
    """
    Класс для тестирования функциональности пользовательского интерфейса.
    """

    def setUp(self):
        """
        Настройка перед тестами.
        """
        self.test_companies_vacancies_count = [
            {"company_name": "Company 1", "vacancy_count": 5},
            {"company_name": "Company 2", "vacancy_count": 3},
        ]

        self.test_all_vacancies = [
            {
                "company_name": "Company 1",
                "vacancy_name": "Python Developer",
                "salary": "100000 - 150000 ₽",
                "url": "https://hh.ru/vacancy/v1",
            },
            {
                "company_name": "Company 2",
                "vacancy_name": "JavaScript Developer",
                "salary": "от 120000 ₽",
                "url": "https://hh.ru/vacancy/v2",
            },
        ]

        self.test_avg_salary = {
            "avg_min_salary": 110000,
            "avg_max_salary": 160000,
            "avg_overall": 135000,
        }

        self.test_higher_salary_vacancies = [
            {
                "company_name": "Company 1",
                "vacancy_name": "Senior Python Developer",
                "salary": "150000 - 200000 ₽",
                "url": "https://hh.ru/vacancy/v3",
            }
        ]

        self.test_keyword_vacancies = [
            {
                "company_name": "Company 1",
                "vacancy_name": "Python Developer",
                "salary": "100000 - 150000 ₽",
                "url": "https://hh.ru/vacancy/v1",
            }
        ]

    def test_display_companies_and_vacancies(self):
        """
        Тестирование функции display_companies_and_vacancies.
        """
        captured_output = io.StringIO()
        sys.stdout = captured_output

        display_companies_and_vacancies(self.test_companies_vacancies_count)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("Company 1: 5 вакансий", output)
        self.assertIn("Company 2: 3 вакансий", output)

    def test_display_all_vacancies(self):
        """
        Тестирование функции display_all_vacancies.
        """
        captured_output = io.StringIO()
        sys.stdout = captured_output

        display_all_vacancies(self.test_all_vacancies)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("Компания: Company 1", output)
        self.assertIn("Вакансия: Python Developer", output)
        self.assertIn("Зарплата: 100000 - 150000 ₽", output)
        self.assertIn("URL: https://hh.ru/vacancy/v1", output)

        self.assertIn("Компания: Company 2", output)
        self.assertIn("Вакансия: JavaScript Developer", output)
        self.assertIn("Зарплата: от 120000 ₽", output)
        self.assertIn("URL: https://hh.ru/vacancy/v2", output)

    def test_display_avg_salary(self):
        """
        Тестирование функции display_avg_salary.
        """
        captured_output = io.StringIO()
        sys.stdout = captured_output

        display_avg_salary(self.test_avg_salary)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("Средняя минимальная зарплата: 110000 ₽", output)
        self.assertIn("Средняя максимальная зарплата: 160000 ₽", output)
        self.assertIn("Средняя зарплата по всем вакансиям: 135000 ₽", output)

    def test_display_higher_salary_vacancies(self):
        """
        Тестирование функции display_higher_salary_vacancies.
        """
        captured_output = io.StringIO()
        sys.stdout = captured_output

        display_higher_salary_vacancies(self.test_higher_salary_vacancies)

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("Вакансии с зарплатой выше средней (1 шт.)", output)
        self.assertIn("Компания: Company 1", output)
        self.assertIn("Вакансия: Senior Python Developer", output)
        self.assertIn("Зарплата: 150000 - 200000 ₽", output)
        self.assertIn("URL: https://hh.ru/vacancy/v3", output)

    def test_display_keyword_vacancies(self):
        """
        Тестирование функции display_keyword_vacancies.
        """
        captured_output = io.StringIO()
        sys.stdout = captured_output

        display_keyword_vacancies(self.test_keyword_vacancies, "Python")

        sys.stdout = sys.__stdout__

        output = captured_output.getvalue()
        self.assertIn("Вакансии, содержащие 'Python' (1 шт.)", output)
        self.assertIn("Компания: Company 1", output)
        self.assertIn("Вакансия: Python Developer", output)
        self.assertIn("Зарплата: 100000 - 150000 ₽", output)
        self.assertIn("URL: https://hh.ru/vacancy/v1", output)

    @patch("builtins.input")
    @patch("src.interface.DBManager")
    def test_run_user_interface(self, mock_db_manager_class, mock_input):
        """
        Тестирование функции run_user_interface.
        """
        mock_db_manager = MagicMock()
        mock_db_manager_class.return_value = mock_db_manager

        mock_db_manager.get_companies_and_vacancies_count.return_value = (
            self.test_companies_vacancies_count
        )
        mock_db_manager.get_all_vacancies.return_value = self.test_all_vacancies
        mock_db_manager.get_avg_salary.return_value = self.test_avg_salary
        mock_db_manager.get_vacancies_with_higher_salary.return_value = (
            self.test_higher_salary_vacancies
        )
        mock_db_manager.get_vacancies_with_keyword.return_value = (
            self.test_keyword_vacancies
        )

        mock_input.side_effect = ["1", "2", "3", "4", "5", "Python", "0"]

        captured_output = io.StringIO()
        sys.stdout = captured_output

        run_user_interface()

        sys.stdout = sys.__stdout__

        mock_db_manager_class.assert_called_once()
        mock_db_manager.get_companies_and_vacancies_count.assert_called_once()
        mock_db_manager.get_all_vacancies.assert_called_once()
        mock_db_manager.get_avg_salary.assert_called_once()
        mock_db_manager.get_vacancies_with_higher_salary.assert_called_once()
        mock_db_manager.get_vacancies_with_keyword.assert_called_once_with("Python")

        self.assertEqual(mock_input.call_count, 7)
        self.assertEqual(mock_input.call_args_list[0], call("\nВыберите пункт меню: "))
        self.assertEqual(
            mock_input.call_args_list[5], call("Введите ключевое слово для поиска: ")
        )
        self.assertEqual(mock_input.call_args_list[6], call("\nВыберите пункт меню: "))

        output = captured_output.getvalue()
        self.assertIn("=== Меню ===", output)
        self.assertIn("1. Показать список компаний и количество вакансий", output)
        self.assertIn("До свидания!", output)


if __name__ == "__main__":
    unittest.main()
