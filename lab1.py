import logging
import sys
import math

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


def analyze_triangle(str_a: str, str_b: str, str_c: str):
    try:
        a = float(str_a)
        b = float(str_b)
        c = float(str_c)
    except ValueError:
        logging.error(f"Невалидные данные: A='{str_a}', B='{str_b}', C='{str_c}'")
        return "", [(-2, -2), (-2, -2), (-2, -2)]

    if a <= 0 or b <= 0 or c <= 0:
        logging.warning(f"Стороны должны быть положительными: A={a}, B={b}, C={c}")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    if a + b <= c or a + c <= b or b + c <= a:
        logging.warning(f"Нарушено неравенство треугольника: A={a}, B={b}, C={c}")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    if math.isclose(a, b) and math.isclose(b, c):
        tri_type = "равносторонний"
    elif math.isclose(a, b) or math.isclose(b, c) or math.isclose(a, c):
        tri_type = "равнобедренный"
    else:
        tri_type = "разносторонний"

    x1, y1 = 0.0, 0.0
    x2, y2 = c, 0.0

    x3 = (a ** 2 + c ** 2 - b ** 2) / (2 * c)
    y3 = math.sqrt(max(0.0, a ** 2 - x3 ** 2))

    coords = [
        (int(round(x1)), int(round(y1))),
        (int(round(x2)), int(round(y2))),
        (int(round(x3)), int(round(y3)))
    ]

    logging.info(f"Успешный запрос: стороны A={a}, B={b}, C={c}, тип='{tri_type}', координаты={coords}")
    return tri_type, coords


if __name__ == "__main__":
    logging.info("Приложение запущено")

    analyze_triangle("10", "10", "10")

    analyze_triangle("3", "4", "5")

    analyze_triangle("5", "8", "5")

    analyze_triangle("5", "abc", "5")

    analyze_triangle("1", "1", "3")

    analyze_triangle("-5", "5", "5")

    while True:
        a = input("Введите сторону a или q чтобы выйти ")
        if a.lower() == ('q'):
            logging.info("Завершение работы по команде ")
            print("Завершение работы.")
            break
        b = input("Введите сторону b ")
        c = input("Введите сторону c ")

        type, coord = analyze_triangle(a, b, c)
        print("Тип треугольника: ", type)
        print("Координаты: ", coord)
