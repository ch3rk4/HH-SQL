"""
Модуль для тестирования функций работы с базой данных.
"""
import unittest
from unittest.mock import patch, MagicMock, call
from src.database import create_database, create_tables, save_employers_to_db, save_vacancies_to_db, connect_to_db


class TestDatabase(unittest.TestCase):
    """
    Класс для тестирования функций работы с базой данных.
    """

    def setUp(self):
        """
        Настройка для тестов.
        """
        self.test_employers = [
            {
                "id": "1234",
                "name": "Test Company 1",
                "url": "https://hh.ru/employer/1234",
                "description": "Test description 1",
                "area": "Moscow",
                "site_url": "https://testcompany1.com",
                "industry": "IT"
            },
            {
                "id": "5678",
                "name": "Test Company 2",
                "url": "https://hh.ru/employer/5678",
                "description": "Test description 2",
                "area": "Saint Petersburg",
                "site_url": "https://testcompany2.com",
                "industry": "Finance"
            }
        ]

        self.test_vacancies = [
            {
                "id": "v1",
                "employer_id": "1234",
                "name": "Python Developer",
                "area": "Moscow",
                "url": "https://hh.ru/vacancy/v1",
                "min_salary": 100000,
                "max_salary": 150000,
                "currency": "RUB",
                "published_at": "2023-01-01T12:00:00+0300",
                "requirement": "Python, Django",
                "responsibility": "Development"
            },
            {
                "id": "v2",
                "employer_id": "5678",
                "name": "JavaScript Developer",
                "area": "Saint Petersburg",
                "url": "https://hh.ru/vacancy/v2",
                "min_salary": 120000,
                "max_salary": 180000,
                "currency": "RUB",
                "published_at": "2023-01-02T12:00:00+0300",
                "requirement": "JavaScript, React",
                "responsibility": "Frontend Development"
            }
        ]

    @patch('psycopg2.connect')
    def test_create_database(self, mock_connect):
        """
        Тестирование функции create_database.
        """
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_connect.return_value = mock_conn

        mock_cur.fetchone.return_value = None

        create_database()

        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()

        expected_calls = [
            call("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", ('headhunter_vacancies',)),
        ]

        self.assertEqual(mock_cur.execute.call_args_list[0], expected_calls[0])

        self.assertEqual(mock_cur.execute.call_count, 2)

        mock_conn.autocommit = True
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.database.connect_to_db')
    def test_create_tables(self, mock_connect_to_db):
        """
        Тестирование функции create_tables.
        """
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect_to_db.return_value = (mock_conn, mock_cur)

        create_tables()

        mock_connect_to_db.assert_called_once()
        self.assertEqual(mock_cur.execute.call_count, 2)
        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.database.connect_to_db')
    def test_save_employers_to_db(self, mock_connect_to_db):
        """
        Тестирование функции save_employers_to_db.
        """
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect_to_db.return_value = (mock_conn, mock_cur)

        save_employers_to_db(self.test_employers)

        mock_connect_to_db.assert_called_once()
        self.assertEqual(mock_cur.execute.call_count, 2)

        args1, kwargs1 = mock_cur.execute.call_args_list[0]
        self.assertIn("INSERT INTO employers", args1[0])
        self.assertEqual(args1[1][0], "1234")
        self.assertEqual(args1[1][1], "Test Company 1")

        args2, kwargs2 = mock_cur.execute.call_args_list[1]
        self.assertIn("INSERT INTO employers", args2[0])
        self.assertEqual(args2[1][0], "5678")
        self.assertEqual(args2[1][1], "Test Company 2")

        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('src.database.connect_to_db')
    def test_save_vacancies_to_db(self, mock_connect_to_db):
        """
        Тестирование функции save_vacancies_to_db.
        """
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect_to_db.return_value = (mock_conn, mock_cur)

        save_vacancies_to_db(self.test_vacancies)

        mock_connect_to_db.assert_called_once()
        self.assertEqual(mock_cur.execute.call_count, 2)  # Должны быть два вызова для вставки двух записей

        args1, kwargs1 = mock_cur.execute.call_args_list[0]
        self.assertIn("INSERT INTO vacancies", args1[0])
        self.assertEqual(args1[1][0], "v1")
        self.assertEqual(args1[1][1], "1234")
        self.assertEqual(args1[1][2], "Python Developer")

        args2, kwargs2 = mock_cur.execute.call_args_list[1]
        self.assertIn("INSERT INTO vacancies", args2[0])
        self.assertEqual(args2[1][0], "v2")
        self.assertEqual(args2[1][1], "5678")
        self.assertEqual(args2[1][2], "JavaScript Developer")

        mock_cur.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch('psycopg2.connect')
    def test_connect_to_db(self, mock_connect):
        """
        Тестирование функции connect_to_db.
        """
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_conn.cursor.return_value = mock_cur
        mock_connect.return_value = mock_conn

        conn, cur = connect_to_db()

        self.assertEqual(conn, mock_conn)
        self.assertEqual(cur, mock_cur)

        mock_connect.assert_called_once_with(
            user='postgres',
            password='your_password',
            host='localhost',
            port='5432',
            database='headhunter_vacancies'
        )
        mock_conn.cursor.assert_called_once()
        self.assertTrue(mock_conn.autocommit)


if __name__ == "__main__":
    unittest.main()