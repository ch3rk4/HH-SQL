"""
Модуль для тестирования основного скрипта main.py.
"""
import unittest
from unittest.mock import patch, MagicMock, call
import sys
import io
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import init_database, fetch_and_save_data, main


class TestMain(unittest.TestCase):
    """
    Класс для тестирования функциональности основного скрипта.
    """

    @patch('main.create_tables')
    @patch('main.create_database')
    def test_init_database(self, mock_create_database, mock_create_tables):
        """
        Тестирование функции init_database.
        """
        captured_output = io.StringIO()
        sys.stdout = captured_output

        init_database()

        sys.stdout = sys.__stdout__

        mock_create_database.assert_called_once()
        mock_create_tables.assert_called_once()

        output = captured_output.getvalue()
        self.assertIn("Инициализация базы данных...", output)

    @patch('main.save_vacancies_to_db')
    @patch('main.save_employers_to_db')
    @patch('main.HeadHunterAPI')
    def test_fetch_and_save_data(self, mock_hh_api_class, mock_save_employers, mock_save_vacancies):
        """
        Тестирование функции fetch_and_save_data.
        """
        mock_hh_api = MagicMock()
        mock_hh_api_class.return_value = mock_hh_api

        test_company_data = {
            "1234": {
                "company": {
                    "id": "1234",
                    "name": "Test Company",
                    "alternate_url": "https://hh.ru/employer/1234",
                    "description": "Test description",
                    "area": {"name": "Moscow"},
                    "site_url": "https://testcompany.com",
                    "industries": [{"name": "IT"}]
                },
                "vacancies": [
                    {
                        "id": "v1",
                        "name": "Python Developer",
                        "area": {"name": "Moscow"},
                        "alternate_url": "https://hh.ru/vacancy/v1",
                        "salary": {
                            "from": 100000,
                            "to": 150000,
                            "currency": "RUB"
                        },
                        "published_at": "2023-01-01T12:00:00+0300",
                        "snippet": {
                            "requirement": "Python, Django",
                            "responsibility": "Development"
                        }
                    }
                ]
            }
        }

        mock_hh_api.get_companies_and_vacancies.return_value = test_company_data

        captured_output = io.StringIO()
        sys.stdout = captured_output

        fetch_and_save_data()

        sys.stdout = sys.__stdout__

        mock_hh_api_class.assert_called_once()
        mock_hh_api.get_companies_and_vacancies.assert_called_once()
        mock_save_employers.assert_called_once()
        mock_save_vacancies.assert_called_once()

        output = captured_output.getvalue()
        self.assertIn("Получение данных из API HeadHunter...", output)
        self.assertIn("Сохранение данных в базу данных...", output)
        self.assertIn("Данные сохранены:", output)

    @patch('main.run_user_interface')
    @patch('main.fetch_and_save_data')
    @patch('main.init_database')
    @patch('time.sleep')
    def test_main(self, mock_sleep, mock_init_database, mock_fetch_and_save_data, mock_run_user_interface):
        """
        Тестирование функции main.
        """
        captured_output = io.StringIO()
        sys.stdout = captured_output

        main()

        sys.stdout = sys.__stdout__

        mock_init_database.assert_called_once()
        mock_fetch_and_save_data.assert_called_once()
        mock_run_user_interface.assert_called_once()
        mock_sleep.assert_called_once()

        output = captured_output.getvalue()
        self.assertIn("=== База данных вакансий HeadHunter ===", output)
        self.assertIn("База данных инициализирована и заполнена данными.", output)


if __name__ == "__main__":
    unittest.main()