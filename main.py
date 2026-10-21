import logging
import sys
import os

os.makedirs("logs", exist_ok=True)

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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.calculator import TriangleCalculator
from src.database import TriangleDatabase
from src.interactions import ConsoleUserInteraction, MockNotificationService
from src.controller import TriangleController


if __name__ == "__main__":
    logging.info("Приложение запущено")

    calculator = TriangleCalculator()
    database = TriangleDatabase("triangles.db")
    user_interaction = ConsoleUserInteraction()
    external_service = MockNotificationService()

    controller = TriangleController(
        calculator,
        database,
        user_interaction,
        external_service
    )

    try:
        controller.run()
    finally:
        database.close()
        logging.info("Приложение завершено")