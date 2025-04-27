"""
Модуль, содержащий класс DBManager для операций с базой данных.
"""

from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extensions import connection

from src.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


class DBManager:
    """
    Класс для управления операциями с базой данных.
    """

    def __init__(self) -> None:
        """
        Инициализация DBManager с параметрами подключения к базе данных.
        """
        self.params = {
            "dbname": DB_NAME,
            "user": DB_USER,
            "password": DB_PASSWORD,
            "host": DB_HOST,
            "port": DB_PORT,
        }

    def _connect(self) -> connection:
        """
        Создание подключения к базе данных.
        """
        return psycopg2.connect(**self.params)

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """
        Получение списка всех компаний и количества вакансий для каждой компании.
        """
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(
                """
            SELECT e.name, COUNT(v.id) as vacancy_count
            FROM employers e
            LEFT JOIN vacancies v ON e.id = v.employer_id
            GROUP BY e.name
            ORDER BY vacancy_count DESC
            """
            )

            results = []
            for row in cur.fetchall():
                results.append({"company_name": row[0], "vacancy_count": row[1]})

        conn.close()
        return results

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получение списка всех вакансий с названием компании, названием вакансии, зарплатой и URL.
        """
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(
                """
            SELECT
                e.name as company_name,
                v.name as vacancy_name,
                v.min_salary,
                v.max_salary,
                v.currency,
                v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.id
            ORDER BY e.name, v.name
            """
            )

            results = []
            for row in cur.fetchall():
                salary_info = self._format_salary(row[2], row[3], row[4])

                results.append(
                    {
                        "company_name": row[0],
                        "vacancy_name": row[1],
                        "salary": salary_info,
                        "url": row[5],
                    }
                )

        conn.close()
        return results

    def get_avg_salary(self) -> Dict[str, Any]:
        """
        Получение средней зарплаты по всем вакансиям.
        """
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(
                """
            SELECT AVG(min_salary)
            FROM vacancies
            WHERE min_salary IS NOT NULL
            """
            )
            avg_min = cur.fetchone()[0]

            cur.execute(
                """
            SELECT AVG(max_salary)
            FROM vacancies
            WHERE max_salary IS NOT NULL
            """
            )
            avg_max = cur.fetchone()[0]

            cur.execute(
                """
            SELECT
                AVG(
                    CASE
                        WHEN min_salary IS NOT NULL AND max_salary IS NOT NULL THEN (min_salary + max_salary) / 2
                        WHEN min_salary IS NOT NULL THEN min_salary
                        WHEN max_salary IS NOT NULL THEN max_salary
                        ELSE NULL
                    END
                ) as overall_avg
            FROM vacancies
            WHERE min_salary IS NOT NULL OR max_salary IS NOT NULL
            """
            )
            overall_avg = cur.fetchone()[0]

        conn.close()

        return {
            "avg_min_salary": int(avg_min) if avg_min else None,
            "avg_max_salary": int(avg_max) if avg_max else None,
            "avg_overall": int(overall_avg) if overall_avg else None,
        }

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """
        Получение вакансий с зарплатой выше средней.
        """
        avg_salary = self.get_avg_salary()
        avg_overall = avg_salary.get("avg_overall", 0)

        if not avg_overall:
            return []

        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(
                """
            SELECT
                e.name as company_name,
                v.name as vacancy_name,
                v.min_salary,
                v.max_salary,
                v.currency,
                v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.id
            WHERE
                (v.min_salary > %s) OR
                (v.max_salary > %s AND v.min_salary IS NULL) OR
                (v.min_salary IS NOT NULL AND v.max_salary IS NOT NULL AND (v.min_salary + v.max_salary) / 2 > %s)
            ORDER BY
                CASE
                    WHEN v.min_salary IS NOT NULL AND v.max_salary IS NOT NULL THEN (v.min_salary + v.max_salary) / 2
                    WHEN v.min_salary IS NOT NULL THEN v.min_salary
                    WHEN v.max_salary IS NOT NULL THEN v.max_salary
                    ELSE 0
                END DESC
            """,
                (avg_overall, avg_overall, avg_overall),
            )

            results = []
            for row in cur.fetchall():
                salary_info = self._format_salary(row[2], row[3], row[4])

                results.append(
                    {
                        "company_name": row[0],
                        "vacancy_name": row[1],
                        "salary": salary_info,
                        "url": row[5],
                    }
                )

        conn.close()
        return results

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получение вакансий, содержащих указанное ключевое слово в названии.
        """
        conn = self._connect()
        with conn.cursor() as cur:
            cur.execute(
                """
            SELECT
                e.name as company_name,
                v.name as vacancy_name,
                v.min_salary,
                v.max_salary,
                v.currency,
                v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.id
            WHERE v.name ILIKE %s
            ORDER BY e.name, v.name
            """,
                (f"%{keyword}%",),
            )

            results = []
            for row in cur.fetchall():
                salary_info = self._format_salary(row[2], row[3], row[4])

                results.append(
                    {
                        "company_name": row[0],
                        "vacancy_name": row[1],
                        "salary": salary_info,
                        "url": row[5],
                    }
                )

        conn.close()
        return results

    def _format_salary(
        self,
        min_salary: Optional[int],
        max_salary: Optional[int],
        currency: Optional[str],
    ) -> str:
        """
        Форматирование информации о зарплате для отображения.
        """
        if min_salary is None and max_salary is None:
            return "Не указана"

        currency_symbol = "₽" if currency == "RUB" else currency

        if min_salary is not None and max_salary is not None:
            return f"{min_salary} - {max_salary} {currency_symbol}"
        elif min_salary is not None:
            return f"от {min_salary} {currency_symbol}"
        else:
            return f"до {max_salary} {currency_symbol}"
