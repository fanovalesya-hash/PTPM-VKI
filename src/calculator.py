import logging
import math

class TriangleCalculator:
    def analyze_triangle(self, str_a: str, str_b: str, str_c: str):
        try:
            a = float(str_a)
            b = float(str_b)
            c = float(str_c)
        except (ValueError, TypeError):
            logging.error(f"Невалидные данные: A='{str_a}', B='{str_b}', C='{str_c}'")
            return "", [(-2, -2), (-2, -2), (-2, -2)]

        if a <= 0 or b <= 0 or c <= 0:
            logging.warning(f"Стороны должны быть положительными: A={a}, B={b}, C={c}")
            return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

        if round(a + b, 1) <= round(c, 1) or round(a + c, 1) <= round(b, 1) or round(b + c, 1) <= round(a, 1):
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

        logging.info(f"Успешный запрос: стороны A={a}, B={b}, C={c}, "
                     f"тип='{tri_type}', координаты={coords}")
        return tri_type, coords