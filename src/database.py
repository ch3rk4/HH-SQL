"""
Модуль для операций с базой данных.
Отвечает за создание базы данных и таблиц.
"""

from typing import Any, Dict, List, Tuple

import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection, cursor

from src.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


def create_database() -> None:
    """
    Создание базы данных, если она не существует.
    """
    conn = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database="postgres",
    )
    conn.autocommit = True
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (DB_NAME,))
    exists = cur.fetchone()

    if not exists:
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print(f"База данных {DB_NAME} успешно создана")
    else:
        print(f"База данных {DB_NAME} уже существует")

    cur.close()
    conn.close()


def connect_to_db() -> Tuple[connection, cursor]:
    """
    Подключение к базе данных проекта.
    """
    conn = psycopg2.connect(
        user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, database=DB_NAME
    )
    conn.autocommit = True
    cur = conn.cursor()
    return conn, cur


def create_tables() -> None:
    """
    Создание таблиц для работодателей и вакансий, если они не существуют.
    """
    conn, cur = connect_to_db()

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS employers (
        id VARCHAR(50) PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        url VARCHAR(255),
        description TEXT,
        area VARCHAR(100),
        site_url VARCHAR(255),
        industry VARCHAR(255)
    )
    """
    )

    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS vacancies (
        id VARCHAR(50) PRIMARY KEY,
        employer_id VARCHAR(50) NOT NULL,
        name VARCHAR(255) NOT NULL,
        area VARCHAR(100),
        url VARCHAR(255),
        min_salary INTEGER,
        max_salary INTEGER,
        currency VARCHAR(10),
        published_at TIMESTAMP,
        requirement TEXT,
        responsibility TEXT,
        FOREIGN KEY (employer_id) REFERENCES employers (id) ON DELETE CASCADE
    )
    """
    )

    print("Таблицы успешно созданы")

    cur.close()
    conn.close()


def save_employers_to_db(employers: List[Dict[str, Any]]) -> None:
    """
    Сохранение данных о работодателях в базу данных.
    """
    conn, cur = connect_to_db()

    for employer in employers:
        cur.execute(
            """
        INSERT INTO employers (id, name, url, description, area, site_url, industry)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            url = EXCLUDED.url,
            description = EXCLUDED.description,
            area = EXCLUDED.area,
            site_url = EXCLUDED.site_url,
            industry = EXCLUDED.industry
        """,
            (
                employer.get("id"),
                employer.get("name"),
                employer.get("url"),
                employer.get("description"),
                employer.get("area"),
                employer.get("site_url"),
                employer.get("industry"),
            ),
        )

    print(f"Сохранено {len(employers)} работодателей в базу данных")

    cur.close()
    conn.close()


def save_vacancies_to_db(vacancies: List[Dict[str, Any]]) -> None:
    """
    Сохранение данных о вакансиях в базу данных.
    """
    conn, cur = connect_to_db()

    for vacancy in vacancies:
        cur.execute(
            """
        INSERT INTO vacancies (
            id, employer_id, name, area, url,
            min_salary, max_salary, currency,
            published_at, requirement, responsibility
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            employer_id = EXCLUDED.employer_id,
            name = EXCLUDED.name,
            area = EXCLUDED.area,
            url = EXCLUDED.url,
            min_salary = EXCLUDED.min_salary,
            max_salary = EXCLUDED.max_salary,
            currency = EXCLUDED.currency,
            published_at = EXCLUDED.published_at,
            requirement = EXCLUDED.requirement,
            responsibility = EXCLUDED.responsibility
        """,
            (
                vacancy.get("id"),
                vacancy.get("employer_id"),
                vacancy.get("name"),
                vacancy.get("area"),
                vacancy.get("url"),
                vacancy.get("min_salary"),
                vacancy.get("max_salary"),
                vacancy.get("currency"),
                vacancy.get("published_at"),
                vacancy.get("requirement"),
                vacancy.get("responsibility"),
            ),
        )

    print(f"Сохранено {len(vacancies)} вакансий в базу данных")

    cur.close()
    conn.close()
