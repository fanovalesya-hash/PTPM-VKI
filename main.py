import logging
import sys
import os

# Создаем папку для логов
os.makedirs("logs", exist_ok=True)

# Настраиваем логирование
log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
    datefmt=date_format,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/file_txt.log", encoding="utf-8")
    ]
)

# Добавляем путь к src для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.calculator import TriangleCalculator
from src.database import TriangleDatabase
from src.interactions import ConsoleUserInteraction, MockNotificationService
from src.controller import TriangleController


if __name__ == "__main__":
    logging.info("Приложение запущено")

    # Создаем все зависимости
    calculator = TriangleCalculator()
    database = TriangleDatabase("triangles.db")  # БД в файле, чтобы данные сохранялись
    user_interaction = ConsoleUserInteraction()
    external_service = MockNotificationService()

    # Создаем контроллер, передавая ему зависимости
    controller = TriangleController(
        calculator,
        database,
        user_interaction,
        external_service
    )

    try:
        # Запускаем интерактивный цикл
        controller.run()
    finally:
        # Закрываем БД при завершении работы
        database.close()
        logging.info("Приложение завершено")