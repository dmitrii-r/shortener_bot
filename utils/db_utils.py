import logging
import os

import asyncpg
from dotenv import load_dotenv
from hashids import Hashids

load_dotenv()


async def create_connection():
    """
    Создает соединение с базой данных.
    """
    return await asyncpg.connect(
        database=os.getenv("DB_NAME"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("DB_HOST"),
    )


async def close_connection(connection):
    """
    Закрывает соединение с базой данных.
    """
    await connection.close()


async def create_table() -> None:
    """
    Создает таблицу в базе данных, если ее еще не существует.
    """
    conn = await create_connection()
    query = """
        CREATE TABLE IF NOT EXISTS urls (
            id SERIAL PRIMARY KEY,
            long_url TEXT NOT NULL,
            summary TEXT,
            location TEXT,
            description TEXT,
            date_start TEXT,
            date_end TEXT,
            hash_value TEXT DEFAULT '',
            usage_count INT DEFAULT 0
        );
        """

    try:
        await conn.execute(query)
    finally:
        logging.info(f"Таблица создана или уже существует в БД.")
        await close_connection(conn)


async def save_event_to_database(event: dict[str]) -> None:
    """
    Сохранение события в базу данных.
    """
    conn = await create_connection()
    query = """
        INSERT INTO urls (
        long_url, summary, location, description, date_start, date_end
        )
        VALUES ($1, $2, $3, $4, $5, $6)
    """
    try:
        await conn.execute(
            query,
            event["long_url"],
            event["summary"],
            event["location"],
            event["description"],
            event["date_start"],
            event["date_end"],
        )

    finally:
        logging.info(f"Событие {event['summary']} добавлено в БД.")
        await close_connection(conn)


async def get_all_events() -> list[dict[str]] | None:
    """
    Получение списка с названиями и длинными ссылками всех имеющихся событий.
    """
    conn = await create_connection()
    query = """
        SELECT id, summary, long_url FROM urls
    """

    try:
        result = await conn.fetch(query)
        logging.info("Запрошен список событий.")
        return [
            {
                "id": record["id"],
                "summary": record["summary"],
                "long_url": record["long_url"],
            }
            for record in result
        ]

    finally:
        await close_connection(conn)


async def update_usage_count_by_id(event_id: int) -> dict[str]:
    """
    Обновление счетчика использований ссылки по ID события.
    """
    conn = await create_connection()
    query = """
        UPDATE urls
        SET usage_count = usage_count + 1
        WHERE id = $1
        RETURNING summary, long_url
    """

    try:
        result = await conn.fetchrow(query, event_id)
        summary = result["summary"]
        return {"long_url": result["long_url"], "summary": result["summary"]}
    finally:
        logging.info(f"Обновлён счетчик использований для: {summary}.")


async def get_usages_count() -> list[dict[str, str | int]]:
    """
    Получение списка событий со статистикой их использования.
    """
    conn = await create_connection()
    query = """
        SELECT summary, usage_count
        FROM urls
    """

    try:
        result = []
        urls = await conn.fetch(query)
        for url in urls:
            result.append(
                {
                    "summary": url["summary"],
                    "usage_count": url["usage_count"],
                }
            )

        return result
    finally:
        logging.info("Получен список событий со статистикой их использования.")
        await close_connection(conn)


async def get_hash_value(long_url: str) -> str | None:
    """
    Получение хэша для длинной ссылки, если он существует.
    """
    conn = await create_connection()
    query = """
        SELECT hash_value
        FROM urls
        WHERE long_url = $1
    """

    try:
        result = await conn.fetchrow(query, long_url)

        if result:
            hash_value = result["hash_value"]
            logging.info(f"Получен хэш для: {long_url}.")
            return hash_value
        else:
            logging.info(f"Хэш для: {long_url} не найден.")

    finally:
        await close_connection(conn)


async def update_usage_count(hash_value: str) -> None:
    """
    Обновление счетчика использований ссылки.
    """
    conn = await create_connection()
    query = """
        UPDATE urls
        SET usage_count = usage_count + 1
        WHERE hash_value = $1
        RETURNING long_url
    """

    try:
        result = await conn.fetchrow(query, hash_value)
        long_url = result["long_url"]
    finally:
        logging.info(f"Обновлён счетчик использований для: {long_url}.")
        await close_connection(conn)


async def insert_url(long_url: str) -> str:
    """
    Добавление новой записи в базу данных.
    """
    conn = await create_connection()
    insert_query = """
        INSERT INTO urls (long_url) VALUES ($1)
        RETURNING id
    """
    update_query = """
        UPDATE urls
        SET hash_value = $1
        WHERE id = $2
        RETURNING hash_value
    """
    hashids = Hashids(
        salt=os.getenv("HASHIDS_SALT"),
        min_length=os.getenv("HASHIDS_MIN_LENGTH"),
    )

    try:
        url_id = await conn.fetchval(insert_query, long_url)
        hash_value = hashids.encode(url_id)
        updated_hash_value = await conn.fetchrow(
            update_query, hash_value, url_id
        )

        return updated_hash_value["hash_value"]
    finally:
        logging.info(f"Ссылка {long_url} добавлена в БД.")
        await close_connection(conn)


async def get_all_urls() -> list[dict[str, str | int]]:
    """
    Получение списка всех коротких ссылок со статистикой использования.
    """
    conn = await create_connection()
    query = """
        SELECT hash_value, usage_count
        FROM urls
    """

    try:
        result = []
        urls = await conn.fetch(query)
        for url in urls:
            result.append(
                {
                    "hash_value": url["hash_value"],
                    "usage_count": url["usage_count"],
                }
            )

        return result
    finally:
        logging.info(
            f"Получен список всех коротких ссылок со статистикой "
            f"их использования."
        )
        await close_connection(conn)
