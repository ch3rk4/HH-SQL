"""
Модуль для тестирования класса DBManager.
"""
import unittest
from unittest.mock import patch, MagicMock, call
import psycopg2
from src.db_manager import DBManager
from src.config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT


class TestDBManager(unittest.TestCase):
    """
    Класс для тестирования функциональности DBManager.
    """

    def setUp(self):
        """
        Настройка перед тестами.
        """
        self.db_manager = DBManager()

        self.test_companies_vacancies_count = [
            {"company_name": "Company 1", "vacancy_count": 5},
            {"company_name": "Company 2", "vacancy_count": 3}
        ]

        self.test_all_vacancies = [
            {
                "company_name": "Company 1",
                "vacancy_name": "Python Developer",
                "salary": "100000 - 150000 ₽",
                "url": "https://hh.ru/vacancy/v1"
            },
            {
                "company_name": "Company 2",
                "vacancy_name": "JavaScript Developer",
                "salary": "от 120000 ₽",
                "url": "https://hh.ru/vacancy/v2"
            }
        ]

        self.test_avg_salary = {
            "avg_min_salary": 110000,
            "avg_max_salary": 160000,
            "avg_overall": 135000
        }

        self.test_higher_salary_vacancies = [
            {
                "company_name": "Company 1",
                "vacancy_name": "Senior Python Developer",
                "salary": "150000 - 200000 ₽",
                "url": "https://hh.ru/vacancy/v3"
            }
        ]

        self.test_keyword_vacancies = [
            {
                "company_name": "Company 1",
                "vacancy_name": "Python Developer",
                "salary": "100000 - 150000 ₽",
                "url": "https://hh.ru/vacancy/v1"
            }
        ]

    @patch('psycopg2.connect')
    def test_connect(self, mock_connect):
        """
        Тестирование метода _connect.
        """
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        conn = self.db_manager._connect()

        self.assertEqual(conn, mock_connect.return_value)

        mock_connect.assert_called_once_with(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )

    @patch('src.db_manager.DBManager._connect')
    def test_get_companies_and_vacancies_count(self, mock_connect):
        """
        Тестирование метода get_companies_and_vacancies_count.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            ("Company 1", 5),
            ("Company 2", 3)
        ]

        result = self.db_manager.get_companies_and_vacancies_count()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["company_name"], "Company 1")
        self.assertEqual(result[0]["vacancy_count"], 5)
        self.assertEqual(result[1]["company_name"], "Company 2")
        self.assertEqual(result[1]["vacancy_count"], 3)

        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.db_manager.DBManager._connect')
    def test_get_all_vacancies(self, mock_connect):
        """
        Тестирование метода get_all_vacancies.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            ("Company 1", "Python Developer", 100000, 150000, "RUB", "https://hh.ru/vacancy/v1"),
            ("Company 2", "JavaScript Developer", 120000, None, "RUB", "https://hh.ru/vacancy/v2")
        ]

        result = self.db_manager.get_all_vacancies()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["company_name"], "Company 1")
        self.assertEqual(result[0]["vacancy_name"], "Python Developer")
        self.assertEqual(result[0]["salary"], "100000 - 150000 ₽")
        self.assertEqual(result[0]["url"], "https://hh.ru/vacancy/v1")

        self.assertEqual(result[1]["company_name"], "Company 2")
        self.assertEqual(result[1]["vacancy_name"], "JavaScript Developer")
        self.assertEqual(result[1]["salary"], "от 120000 ₽")
        self.assertEqual(result[1]["url"], "https://hh.ru/vacancy/v2")

        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.db_manager.DBManager._connect')
    def test_get_avg_salary(self, mock_connect):
        """
        Тестирование метода get_avg_salary.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchone.side_effect = [(110000.0,), (160000.0,), (135000.0,)]

        result = self.db_manager.get_avg_salary()

        self.assertEqual(result["avg_min_salary"], 110000)
        self.assertEqual(result["avg_max_salary"], 160000)
        self.assertEqual(result["avg_overall"], 135000)

        mock_connect.assert_called_once()
        self.assertEqual(mock_cursor.execute.call_count, 3)
        self.assertEqual(mock_cursor.fetchone.call_count, 3)
        mock_conn.close.assert_called_once()

    @patch('src.db_manager.DBManager.get_avg_salary')
    @patch('src.db_manager.DBManager._connect')
    def test_get_vacancies_with_higher_salary(self, mock_connect, mock_get_avg_salary):
        """
        Тестирование метода get_vacancies_with_higher_salary.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_get_avg_salary.return_value = self.test_avg_salary

        mock_cursor.fetchall.return_value = [
            ("Company 1", "Senior Python Developer", 150000, 200000, "RUB", "https://hh.ru/vacancy/v3")
        ]

        result = self.db_manager.get_vacancies_with_higher_salary()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["company_name"], "Company 1")
        self.assertEqual(result[0]["vacancy_name"], "Senior Python Developer")
        self.assertEqual(result[0]["salary"], "150000 - 200000 ₽")
        self.assertEqual(result[0]["url"], "https://hh.ru/vacancy/v3")

        mock_get_avg_salary.assert_called_once()
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.db_manager.DBManager._connect')
    def test_get_vacancies_with_keyword(self, mock_connect):
        """
        Тестирование метода get_vacancies_with_keyword.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            ("Company 1", "Python Developer", 100000, 150000, "RUB", "https://hh.ru/vacancy/v1")
        ]

        result = self.db_manager.get_vacancies_with_keyword("Python")

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["company_name"], "Company 1")
        self.assertEqual(result[0]["vacancy_name"], "Python Developer")
        self.assertEqual(result[0]["salary"], "100000 - 150000 ₽")
        self.assertEqual(result[0]["url"], "https://hh.ru/vacancy/v1")

        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_cursor.fetchall.assert_called_once()
        mock_conn.close.assert_called_once()

    def test_format_salary(self):
        """
        Тестирование метода _format_salary.
        """
        result = self.db_manager._format_salary(100000, 150000, "RUB")
        self.assertEqual(result, "100000 - 150000 ₽")

        result = self.db_manager._format_salary(100000, None, "RUB")
        self.assertEqual(result, "от 100000 ₽")

        result = self.db_manager._format_salary(None, 150000, "RUB")
        self.assertEqual(result, "до 150000 ₽")

        result = self.db_manager._format_salary(None, None, "RUB")
        self.assertEqual(result, "Не указана")

        result = self.db_manager._format_salary(1000, 2000, "USD")
        self.assertEqual(result, "1000 - 2000 USD")


if __name__ == "__main__":
    unittest.main()