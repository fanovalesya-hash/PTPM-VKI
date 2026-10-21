import logging

class TriangleController:
    def __init__(self, calculator, database, user_interaction, external_service):
        # Сохраняем все зависимости — они придут к нам из main.py или из тестов
        self.calculator = calculator
        self.database = database
        self.user_interaction = user_interaction
        self.external_service = external_service

    def process_triangle(self, str_a: str, str_b: str, str_c: str) -> str:
        """
        Основной метод бизнес-логики.
        Принимает три строки со сторонами, возвращает итоговую строку-результат.
        """
        # Шаг 1: Пытаемся преобразовать строки в float для работы с БД
        try:
            a = float(str_a)
            b = float(str_b)
            c = float(str_c)
        except (ValueError, TypeError):
            # Если ввод невалидный — даже не ходим в БД, сразу формируем ошибку
            result_str = f"Ошибка: невалидные данные ({str_a}, {str_b}, {str_c})"
            self.external_service.send_data(result_str)
            return result_str

        # Шаг 2: Проверяем, есть ли уже такой треугольник в БД
        db_record = self.database.get_record(a, b, c)

        if db_record is not None:
            # Запись найдена — берем результат из БД, не пересчитываем
            tri_type, error_msg = db_record
            logging.info(f"Найдено в БД: стороны {a}, {b}, {c}")
        else:
            # Записи нет — вычисляем через калькулятор
            tri_type, coords = self.calculator.analyze(str_a, str_b, str_c)

            # Определяем сообщение об ошибке (если оно есть)
            if tri_type == "":
                error_msg = "Невалидные данные"
            elif tri_type == "не треугольник":
                error_msg = "Нарушено неравенство треугольника или стороны неположительные"
            else:
                error_msg = ""

            # Сохраняем результат в БД
            self.database.add_record(a, b, c, tri_type, error_msg)

        # Шаг 3: Формируем строку-результат для пользователя и внешнего сервиса
        if tri_type == "":
            result_str = f"Ошибка обработки: стороны ({a}, {b}, {c})"
        elif tri_type == "не треугольник":
            result_str = f"Не треугольник: стороны ({a}, {b}, {c})"
        else:
            _, coords = self.calculator.analyze(str_a, str_b, str_c)
            result_str = f"Треугольник {tri_type}: {coords}"

        # Шаг 4: Отправляем результат во внешний сервис (имитация)
        self.external_service.send_data(result_str)

        return result_str

    def run(self):
        """
        Запуск интерактивного цикла работы с пользователем.
        """
        logging.info("Контроллер запущен")
        print("=== Анализатор треугольников ===")
        print("Для выхода введите 'q' вместо стороны A")

        while True:
            # Запрашиваем данные через абстрактный интерфейс
            a = self.user_interaction.get_input("Введите сторону A (или 'q' для выхода): ")

            if a.lower() == 'q':
                logging.info("Пользователь завершил работу")
                print("Завершение работы.")
                break

            b = self.user_interaction.get_input("Введите сторону B: ")
            c = self.user_interaction.get_input("Введите сторону C: ")

            # Обрабатываем треугольник и выводим результат
            result = self.process_triangle(a, b, c)
            print(f"Результат: {result}\n")