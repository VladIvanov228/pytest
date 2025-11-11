"""
Тесты для калькулятора обратной польской нотации
"""

import pytest  # pylint: disable=import-error
from rpn_calculator import RPNCalculator


class TestRPNCalculator:
    """Тесты для RPNCalculator"""

    @pytest.fixture
    def calculator(self):
        """Создает экземпляр калькулятора для тестов"""
        return RPNCalculator()

    def test_tokenize(self, calculator):
        """Тест токенизации выражений"""
        assert calculator.tokenize("2+3") == ['2', '+', '3']
        assert calculator.tokenize("(2+3)*4") == ['(', '2', '+', '3', ')', '*', '4']
        assert calculator.tokenize("10.5 - 2.3") == ['10.5', '-', '2.3']
        assert calculator.tokenize("2^3^2") == ['2', '^', '3', '^', '2']

    def test_is_number(self, calculator):
        """Тест проверки чисел"""
        assert calculator.is_number("123") is True
        assert calculator.is_number("12.34") is True
        assert calculator.is_number("0.5") is True
        assert calculator.is_number("+") is False
        assert calculator.is_number("(") is False

    def test_shunting_yard_simple(self, calculator):
        """Тест преобразования простых выражений в RPN"""
        assert calculator.shunting_yard("2+3") == ['2', '3', '+']
        assert calculator.shunting_yard("2-3") == ['2', '3', '-']
        assert calculator.shunting_yard("2*3") == ['2', '3', '*']
        assert calculator.shunting_yard("2/3") == ['2', '3', '/']

    def test_shunting_yard_precedence(self, calculator):
        """Тест приоритета операций"""
        assert calculator.shunting_yard("2+3*4") == ['2', '3', '4', '*', '+']
        assert calculator.shunting_yard("2*3+4") == ['2', '3', '*', '4', '+']
        assert calculator.shunting_yard("2+3+4") == ['2', '3', '+', '4', '+']

    def test_shunting_yard_parentheses(self, calculator):
        """Тест скобок"""
        assert calculator.shunting_yard("(2+3)*4") == ['2', '3', '+', '4', '*']
        assert calculator.shunting_yard("2*(3+4)") == ['2', '3', '4', '+', '*']
        assert calculator.shunting_yard("(2+3)*(4+5)") == ['2', '3', '+', '4', '5', '+', '*']

    def test_shunting_yard_power(self, calculator):
        """Тест операции возведения в степень"""
        assert calculator.shunting_yard("2^3") == ['2', '3', '^']
        # правоассоциативность
        assert calculator.shunting_yard("2^3^2") == ['2', '3', '2', '^', '^']
        assert calculator.shunting_yard("2+3^2") == ['2', '3', '2', '^', '+']

    def test_shunting_yard_complex(self, calculator):
        """Тест сложных выражений"""
        expected = ['3', '4', '2', '*', '1', '5', '-', '2', '^', '/', '+']
        assert calculator.shunting_yard("3+4*2/(1-5)^2") == expected

    def test_evaluate_rpn_simple(self, calculator):
        """Тест вычисления простых RPN выражений"""
        assert calculator.evaluate_rpn(['2', '3', '+']) == 5
        assert calculator.evaluate_rpn(['5', '3', '-']) == 2
        assert calculator.evaluate_rpn(['4', '2', '*']) == 8
        assert calculator.evaluate_rpn(['6', '2', '/']) == 3
        assert calculator.evaluate_rpn(['2', '3', '^']) == 8

    def test_evaluate_rpn_complex(self, calculator):
        """Тест вычисления сложных RPN выражений"""
        # 2 + 3 * 4
        assert calculator.evaluate_rpn(['2', '3', '4', '*', '+']) == 14
        # 3 + 4 * 2 / (1 - 5)^2
        rpn_expr = ['3', '4', '2', '*', '1', '5', '-', '2', '^', '/', '+']
        assert calculator.evaluate_rpn(rpn_expr) == 3.5

    def test_evaluate_rpn_division_by_zero(self, calculator):
        """Тест деления на ноль"""
        with pytest.raises(ValueError, match="Деление на ноль"):
            calculator.evaluate_rpn(['5', '0', '/'])

    def test_calculate_simple(self, calculator):
        """Тест вычисления простых выражений"""
        assert calculator.calculate("2+3") == 5
        assert calculator.calculate("10-4") == 6
        assert calculator.calculate("3*4") == 12
        assert calculator.calculate("15/3") == 5
        assert calculator.calculate("2^3") == 8

    def test_calculate_with_spaces(self, calculator):
        """Тест вычисления выражений с пробелами"""
        assert calculator.calculate("2 + 3") == 5
        assert calculator.calculate(" 10 - 4 ") == 6
        assert calculator.calculate("3 * 4 ") == 12

    def test_calculate_complex(self, calculator):
        """Тест вычисления сложных выражений"""
        assert calculator.calculate("(2+3)*4") == 20
        assert calculator.calculate("2+3*4") == 14
        assert calculator.calculate("3+4*2/(1-5)^2") == 3.5
        # 2^(3^2) = 2^9 = 512
        assert calculator.calculate("2^3^2") == 512

    def test_calculate_float(self, calculator):
        """Тест вычисления с дробными числами"""
        assert calculator.calculate("2.5 + 3.5") == 6.0
        assert calculator.calculate("10.0 / 4.0") == 2.5
        assert calculator.calculate("0.5 * 4") == 2.0

    def test_calculate_empty_expression(self, calculator):
        """Тест пустого выражения"""
        with pytest.raises(ValueError, match="Пустое выражение"):
            calculator.calculate("")

    def test_calculate_invalid_expression(self, calculator):
        """Тест некорректных выражений"""
        with pytest.raises(ValueError, match="Несбалансированные скобки"):
            calculator.calculate("(2+3")

        with pytest.raises(ValueError, match="Несбалансированные скобки"):
            calculator.calculate("2+3)")

    def test_operator_precedence(self, calculator):
        """Тест приоритетов операторов"""
        # Умножение имеет более высокий приоритет чем сложение
        assert calculator.calculate("2+3*4") == 14
        # Степень имеет более высокий приоритет чем умножение
        assert calculator.calculate("2*3^2") == 18
        # Скобки меняют приоритет
        assert calculator.calculate("(2+3)*4") == 20

    def test_operator_popping_logic(self, calculator):
        """Тест логики выталкивания операторов через публичные методы"""
        # Левая ассоциативность: + перед +
        assert calculator.shunting_yard("2+3+4") == ['2', '3', '+', '4', '+']
        # Правая ассоциативность: ^ перед ^
        assert calculator.shunting_yard("2^3^2") == ['2', '3', '2', '^', '^']
        # Высокий приоритет перед низким: * перед +
        assert calculator.shunting_yard("2+3*4") == ['2', '3', '4', '*', '+']
        # Низкий приоритет перед высоким: + после *
        assert calculator.shunting_yard("2*3+4") == ['2', '3', '*', '4', '+']
