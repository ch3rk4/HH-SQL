"""
Модуль для тестирования взаимодействия с API HeadHunter.
"""

import unittest
from unittest.mock import MagicMock, patch

from src.api import (HeadHunterAPI, extract_company_data, extract_vacancy_data,
                     normalize_salary)


class TestHeadHunterAPI(unittest.TestCase):
    """
    Класс для тестирования HeadHunterAPI.
    """

    def setUp(self):
        """
        Настройка для тестов.
        """
        self.api = HeadHunterAPI()

        self.employer_response = {
            "id": "1234",
            "name": "Test Company",
            "alternate_url": "https://hh.ru/employer/1234",
            "description": "Test description",
            "area": {"name": "Moscow"},
            "site_url": "https://testcompany.com",
            "industries": [{"name": "IT"}],
        }

        # Создаем тестовый ответ для вакансий
        self.vacancies_response = {
            "items": [
                {
                    "id": "v1",
                    "name": "Python Developer",
                    "area": {"name": "Moscow"},
                    "alternate_url": "https://hh.ru/vacancy/v1",
                    "salary": {"from": 100000, "to": 150000, "currency": "RUB"},
                    "published_at": "2023-01-01T12:00:00+0300",
                    "snippet": {
                        "requirement": "Python, Django",
                        "responsibility": "Development",
                    },
                }
            ],
            "pages": 1,
        }

    @patch("requests.get")
    def test_get_employer(self, mock_get):
        """
        Тестирование метода get_employer.
        """
        # Настройка мока для имитации ответа API
        mock_response = MagicMock()
        mock_response.json.return_value = self.employer_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Вызов тестируемого метода
        result = self.api.get_employer("1234")

        # Проверка результата
        self.assertEqual(result, self.employer_response)
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_get_employer_vacancies(self, mock_get):
        """
        Тестирование метода get_employer_vacancies.
        """
        # Настройка мока для имитации ответа API
        mock_response = MagicMock()
        mock_response.json.return_value = self.vacancies_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Вызов тестируемого метода
        result = self.api.get_employer_vacancies("1234")

        # Проверка результата
        self.assertEqual(result, self.vacancies_response)
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_get_all_employer_vacancies(self, mock_get):
        """
        Тестирование метода get_all_employer_vacancies.
        """
        # Настройка мока для имитации ответа API
        mock_response = MagicMock()
        mock_response.json.return_value = self.vacancies_response
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Вызов тестируемого метода
        result = self.api.get_all_employer_vacancies("1234")

        # Проверка результата
        self.assertEqual(result, self.vacancies_response["items"])
        mock_get.assert_called_once()

    @patch("requests.get")
    def test_get_companies_and_vacancies(self, mock_get):
        """
        Тестирование метода get_companies_and_vacancies.
        """
        # Настройка мока для имитации ответов API
        mock_response1 = MagicMock()
        mock_response1.json.return_value = self.employer_response
        mock_response1.status_code = 200

        mock_response2 = MagicMock()
        mock_response2.json.return_value = self.vacancies_response
        mock_response2.status_code = 200

        mock_get.side_effect = [mock_response1, mock_response2]

        # Вызов тестируемого метода
        result = self.api.get_companies_and_vacancies(["1234"])

        # Проверка результата
        self.assertIn("1234", result)
        self.assertIn("company", result["1234"])
        self.assertIn("vacancies", result["1234"])
        self.assertEqual(result["1234"]["company"], self.employer_response)
        self.assertEqual(result["1234"]["vacancies"], self.vacancies_response["items"])
        self.assertEqual(
            mock_get.call_count, 2
        )  # Должно быть два вызова: get_employer и get_employer_vacancies

    @patch("requests.get")
    def test_rate_limit_handling(self, mock_get):
        """
        Тестирование обработки ограничения частоты запросов.
        """
        # Настройка моков для имитации ответов API: сначала 429, затем 200
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429

        mock_response_200 = MagicMock()
        mock_response_200.json.return_value = self.employer_response
        mock_response_200.status_code = 200

        mock_get.side_effect = [mock_response_429, mock_response_200]

        # Переопределяем метод sleep, чтобы тест не ждал
        with patch("time.sleep") as mock_sleep:
            # Вызов тестируемого метода
            result = self.api.get_employer("1234")

            # Проверка результата
            self.assertEqual(result, self.employer_response)
            self.assertEqual(
                mock_get.call_count, 2
            )  # Должно быть два вызова: один с 429, второй с 200
            mock_sleep.assert_called_once()  # Должен быть вызов sleep

    def test_normalize_salary(self):
        """
        Тестирование функции normalize_salary.
        """
        # Тестирование с полным объектом зарплаты
        salary_data = {"from": 100000, "to": 150000, "currency": "RUB"}
        result = normalize_salary(salary_data)
        self.assertEqual(result["min_salary"], 100000)
        self.assertEqual(result["max_salary"], 150000)
        self.assertEqual(result["currency"], "RUB")

        # Тестирование с зарплатой в другой валюте
        salary_data = {"from": 1000, "to": 2000, "currency": "USD"}
        result = normalize_salary(salary_data)
        self.assertEqual(result["min_salary"], 75000)  # 1000 * 75
        self.assertEqual(result["max_salary"], 150000)  # 2000 * 75
        self.assertEqual(result["currency"], "RUB")

        # Тестирование с None значениями
        salary_data = {"from": None, "to": 150000, "currency": "RUB"}
        result = normalize_salary(salary_data)
        self.assertIsNone(result["min_salary"])
        self.assertEqual(result["max_salary"], 150000)
        self.assertEqual(result["currency"], "RUB")

        # Тестирование с None объектом зарплаты
        result = normalize_salary(None)
        self.assertIsNone(result["min_salary"])
        self.assertIsNone(result["max_salary"])
        self.assertIsNone(result["currency"])

    def test_extract_vacancy_data(self):
        """
        Тестирование функции extract_vacancy_data.
        """
        vacancy = {
            "id": "v1",
            "name": "Python Developer",
            "area": {"name": "Moscow"},
            "alternate_url": "https://hh.ru/vacancy/v1",
            "salary": {"from": 100000, "to": 150000, "currency": "RUB"},
            "published_at": "2023-01-01T12:00:00+0300",
            "snippet": {
                "requirement": "Python, Django",
                "responsibility": "Development",
            },
        }

        result = extract_vacancy_data(vacancy)

        self.assertEqual(result["id"], "v1")
        self.assertEqual(result["name"], "Python Developer")
        self.assertEqual(result["area"], "Moscow")
        self.assertEqual(result["url"], "https://hh.ru/vacancy/v1")
        self.assertEqual(result["min_salary"], 100000)
        self.assertEqual(result["max_salary"], 150000)
        self.assertEqual(result["currency"], "RUB")
        self.assertEqual(result["published_at"], "2023-01-01T12:00:00+0300")
        self.assertEqual(result["requirement"], "Python, Django")
        self.assertEqual(result["responsibility"], "Development")

    def test_extract_company_data(self):
        """
        Тестирование функции extract_company_data.
        """
        company = {
            "id": "1234",
            "name": "Test Company",
            "alternate_url": "https://hh.ru/employer/1234",
            "description": "Test description",
            "area": {"name": "Moscow"},
            "site_url": "https://testcompany.com",
            "industries": [{"name": "IT"}],
        }

        result = extract_company_data(company)

        self.assertEqual(result["id"], "1234")
        self.assertEqual(result["name"], "Test Company")
        self.assertEqual(result["url"], "https://hh.ru/employer/1234")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(result["area"], "Moscow")
        self.assertEqual(result["site_url"], "https://testcompany.com")
        self.assertEqual(result["industry"], "IT")


if __name__ == "__main__":
    unittest.main()
