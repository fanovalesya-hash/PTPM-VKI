import unittest
from unittest.mock import Mock
import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.controller import TriangleController
from src.calculator import TriangleCalculator
from src.database import TriangleDatabase


class TestTriangleIntegration(unittest.TestCase):

    def setUp(self):
        self.calculator = TriangleCalculator()
        self.database = TriangleDatabase(":memory:")
        self.user_interaction = Mock()
        self.external_service = Mock()

        self.controller = TriangleController(
            self.calculator,
            self.database,
            self.user_interaction,
            self.external_service
        )

    def tearDown(self):
        self.database.close()


    def test_integration_new_triangle_calculated_and_saved(self):
        result = self.controller.process_triangle("3", "4", "5")

        self.assertIn("разносторонний", result)

        db_record = self.database.get_record(3.0, 4.0, 5.0)
        self.assertIsNotNone(db_record)
        self.assertEqual(db_record[0], "разносторонний")

        self.external_service.send_data.assert_called_once()
        call_args = self.external_service.send_data.call_args[0][0]
        self.assertIn("разносторонний", call_args)

    def test_integration_existing_triangle_from_database(self):
        self.database.add_record(10.0, 10.0, 10.0, "равносторонний", "")

        mock_calculator = Mock()
        mock_calculator.analyze_triangle.return_value = (
            "равносторонний",
            [(0, 0), (10, 0), (5, 8)]
        )

        controller_with_mock = TriangleController(
            mock_calculator,
            self.database,
            self.user_interaction,
            self.external_service
        )

        result = controller_with_mock.process_triangle("10", "10", "10")

        mock_calculator.analyze_triangle.assert_called_once()

        self.assertIn("равносторонний", result)

        self.external_service.send_data.assert_called_once()

    def test_integration_invalid_data_not_saved_to_database(self):

        result = self.controller.process_triangle("abc", "4", "5")
        self.assertIn("Ошибка", result)

        db_record = self.database.get_record(0.0, 4.0, 5.0)
        self.assertIsNone(db_record)

        self.external_service.send_data.assert_called_once()
        call_args = self.external_service.send_data.call_args[0][0]
        self.assertIn("Ошибка", call_args)


    def test_database_add_and_get_record(self):
        self.database.add_record(5.0, 5.0, 8.0, "равнобедренный", "")

        record = self.database.get_record(5.0, 5.0, 8.0)

        self.assertIsNotNone(record)
        self.assertEqual(record[0], "равнобедренный")
        self.assertEqual(record[1], "")

    def test_database_delete_record(self):
        self.database.add_record(7.0, 7.0, 7.0, "равносторонний", "")

        record_before = self.database.get_record(7.0, 7.0, 7.0)
        self.assertIsNotNone(record_before)

        self.database.delete_record(7.0, 7.0, 7.0)

        record_after = self.database.get_record(7.0, 7.0, 7.0)
        self.assertIsNone(record_after)


class TestControllerWithMockedInput(unittest.TestCase):

    def test_run_method_with_mocked_input(self):
        calculator = TriangleCalculator()
        database = TriangleDatabase(":memory:")
        user_interaction = Mock()
        external_service = Mock()

        controller = TriangleController(
            calculator,
            database,
            user_interaction,
            external_service
        )

        user_interaction.get_input.side_effect = ["3", "4", "5", "q"]

        controller.run()

        self.assertEqual(user_interaction.get_input.call_count, 4)

        self.assertTrue(external_service.send_data.called)

        database.close()


if __name__ == "__main__":
    unittest.main()