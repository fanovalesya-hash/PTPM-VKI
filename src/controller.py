import logging

class TriangleController:
    def __init__(self, calculator, database, user_interaction, external_service):
        self.calculator = calculator
        self.database = database
        self.user_interaction = user_interaction
        self.external_service = external_service

    def process_triangle(self, str_a: str, str_b: str, str_c: str) -> str:
        try:
            a = float(str_a)
            b = float(str_b)
            c = float(str_c)
        except (ValueError, TypeError):
            result_str = f"Ошибка: невалидные данные ({str_a}, {str_b}, {str_c})"
            self.external_service.send_data(result_str)
            return result_str

        db_record = self.database.get_record(a, b, c)

        if db_record is not None:
            tri_type, error_msg = db_record
            logging.info(f"Найдено в БД: стороны {a}, {b}, {c}")
        else:
            tri_type, coords = self.calculator.analyze_triangle(str_a, str_b, str_c)
            error_msg = "Нарушено неравенство треугольника или стороны неположительные"
            # Сохраняем результат в БД
            self.database.add_record(a, b, c, tri_type, error_msg)


        if tri_type == "не треугольник":
            result_str = f"Не треугольник: стороны ({a}, {b}, {c})"
        else:
            _, coords = self.calculator.analyze_triangle(str_a, str_b, str_c)
            result_str = f"Треугольник {tri_type}: {coords}"
        self.external_service.send_data(result_str)

        return result_str

    def run(self):
        logging.info("Контроллер запущен")
        print("=== Анализатор треугольников ===")
        print("Для выхода введите 'q' вместо стороны A")

        while True:
            a = self.user_interaction.get_input("Введите сторону A (или 'q' для выхода): ")

            if a.lower() == 'q':
                logging.info("Пользователь завершил работу")
                print("Завершение работы.")
                break

            b = self.user_interaction.get_input("Введите сторону B: ")
            c = self.user_interaction.get_input("Введите сторону C: ")

            result = self.process_triangle(a, b, c)
            print(f"Результат: {result}\n")