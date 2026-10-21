import sqlite3
import logging

class TriangleDatabase:
    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path)
        self._create_table()

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS triangles (
                side1 REAL,
                side2 REAL,
                side3 REAL,
                tri_type TEXT,
                error_msg TEXT,
                PRIMARY KEY (side1, side2, side3)
            )
        """)
        self.conn.commit()

    def add_record(self, side1: float, side2: float, side3: float, tri_type: str, error_msg: str):
        cursor = self.conn.cursor()
        try:
            # INSERT OR REPLACE обновит запись, если стороны совпадут (избегаем дубликатов)
            cursor.execute("""
                INSERT OR REPLACE INTO triangles (side1, side2, side3, tri_type, error_msg)
                VALUES (?, ?, ?, ?, ?)
            """, (side1, side2, side3, tri_type, error_msg))
            self.conn.commit()
            logging.info(f"Добавлена/обновлена запись в БД: {side1}, {side2}, {side3}")
        except sqlite3.Error as e:
            logging.error(f"Ошибка БД при добавлении: {e}")

    def get_record(self, side1: float, side2: float, side3: float):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT tri_type, error_msg FROM triangles 
            WHERE side1 = ? AND side2 = ? AND side3 = ?
        """, (side1, side2, side3))
        return cursor.fetchone()  # Вернет кортеж (tri_type, error_msg) или None

    def delete_record(self, side1: float, side2: float, side3: float):
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM triangles WHERE side1 = ? AND side2 = ? AND side3 = ?
        """, (side1, side2, side3))
        self.conn.commit()

    def close(self):
        self.conn.close()