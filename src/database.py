"""
Модуль 1: Библиотека классов для работы с базой данных (SQLite).

Реализует класс DatabaseRepository для хранения комментариев с форума.
"""

import sqlite3
from typing import Optional


# Ограничения на длины строк (из ТЗ)
MAX_NAME_LENGTH = 256
MAX_MESSAGE_LENGTH = 8096


class DatabaseRepository:
    """
    Репозиторий для работы с таблицей comments в SQLite.

    Принимает путь к файлу БД или ':memory:' для тестов.
    """

    def __init__(self, db_path: str = ":memory:") -> None:
        if not isinstance(db_path, str):
            raise TypeError("db_path должен быть строкой")

        self.db_path = db_path
        # check_same_thread=False — чтобы можно было использовать
        # соединение из разных потоков (пригодится, если будем масштабировать)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        # Возвращать строки как dict-подобные объекты (доступ по имени столбца)
        self.connection.row_factory = sqlite3.Row
        self._create_table()

    # ------------------------------------------------------------------ #
    #  Внутренние (приватные) методы
    # ------------------------------------------------------------------ #

    def _create_table(self) -> None:
        """Создаёт таблицу comments, если её ещё нет."""
        cursor = self.connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS comments (
                id      INTEGER PRIMARY KEY,
                name    TEXT NOT NULL,
                message TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    @staticmethod
    def _validate_comment_id(comment_id) -> None:
        """Проверяет, что comment_id — целое число."""
        if not isinstance(comment_id, int) or isinstance(comment_id, bool):
            raise ValueError(
                f"comment_id должен быть целым числом, получено: {type(comment_id).__name__}"
            )

    @staticmethod
    def _validate_username(username) -> None:
        """Проверяет тип и длину username."""
        if not isinstance(username, str):
            raise ValueError(
                f"username должен быть строкой, получено: {type(username).__name__}"
            )
        if not username:
            raise ValueError("username не может быть пустым")
        if len(username) > MAX_NAME_LENGTH:
            raise ValueError(
                f"username превышает {MAX_NAME_LENGTH} символов (получено {len(username)})"
            )

    @staticmethod
    def _validate_message(message) -> None:
        """Проверяет тип и длину message."""
        if not isinstance(message, str):
            raise ValueError(
                f"message должен быть строкой, получено: {type(message).__name__}"
            )
        if not message:
            raise ValueError("message не может быть пустым")
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError(
                f"message превышает {MAX_MESSAGE_LENGTH} символов (получено {len(message)})"
            )

    @staticmethod
    def _row_to_dict(row: Optional[sqlite3.Row]) -> Optional[dict]:
        """Преобразует sqlite3.Row в обычный dict."""
        if row is None:
            return None
        return dict(row)

    # ------------------------------------------------------------------ #
    #  Публичный интерфейс репозитория (5 обязательных методов)
    # ------------------------------------------------------------------ #

    def add(self, comment_id: int, username: str, message: str) -> bool:
        """
        Добавляет новую запись.

        :raises ValueError: при невалидных типах/длинах.
        :raises sqlite3.IntegrityError: при дублировании comment_id.
        :return: True при успехе.
        """
        self._validate_comment_id(comment_id)
        self._validate_username(username)
        self._validate_message(message)

        cursor = self.connection.cursor()
        cursor.execute(
            "INSERT INTO comments (id, name, message) VALUES (?, ?, ?)",
            (comment_id, username, message),
        )
        self.connection.commit()
        return True

    def get_by_id(self, comment_id: int) -> Optional[dict]:
        """
        Возвращает запись по ID или None, если её нет.
        """
        self._validate_comment_id(comment_id)
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, name, message FROM comments WHERE id = ?", (comment_id,))
        return self._row_to_dict(cursor.fetchone())

    def get_by_name(self, username: str) -> list[dict]:
        """
        Возвращает список всех записей, оставленных пользователем username.
        Пустой список — если записей нет.
        """
        if not isinstance(username, str):
            raise ValueError("username должен быть строкой")

        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id, name, message FROM comments WHERE name = ? ORDER BY id",
            (username,),
        )
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def update(self, comment_id: int, new_message: str) -> bool:
        """
        Обновляет поле message у записи с заданным ID.

        :raises ValueError: при невалидном new_message.
        :return: True — если запись обновлена, False — если ID не найден.
        """
        self._validate_comment_id(comment_id)
        self._validate_message(new_message)

        cursor = self.connection.cursor()
        cursor.execute(
            "UPDATE comments SET message = ? WHERE id = ?",
            (new_message, comment_id),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def delete(self, comment_id: int) -> bool:
        """
        Удаляет запись по comment_id.

        :return: True — если запись удалена, False — если ID не найден.
        """
        self._validate_comment_id(comment_id)

        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
        self.connection.commit()
        return cursor.rowcount > 0

    # ------------------------------------------------------------------ #
    #  Утилитарные методы
    # ------------------------------------------------------------------ #

    def close(self) -> None:
        """Закрывает соединение с БД."""
        if self.connection:
            self.connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()