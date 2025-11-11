"""
Калькулятор с преобразованием в обратную польскую нотацию (RPN)
"""

import operator
import re


class RPNCalculator:
    """Калькулятор обратной польской нотации"""

    def __init__(self):
        self.operators = {
            '+': {'precedence': 1, 'associativity': 'left', 'function': operator.add},
            '-': {'precedence': 1, 'associativity': 'left', 'function': operator.sub},
            '*': {'precedence': 2, 'associativity': 'left', 'function': operator.mul},
            '/': {'precedence': 2, 'associativity': 'left', 'function': operator.truediv},
            '^': {'precedence': 3, 'associativity': 'right', 'function': operator.pow}
        }

    def tokenize(self, expression: str) -> list:
        """
        Разбивает выражение на токены (числа, операторы, скобки)

        Args:
            expression: математическое выражение в инфиксной нотации

        Returns:
            Список токенов
        """
        # Регулярное выражение для токенизации
        token_pattern = r'\d+\.?\d*|[()+\-*/^]'
        tokens = re.findall(token_pattern, expression)
        return tokens

    def is_number(self, token: str) -> bool:
        """
        Проверяет, является ли токен числом

        Args:
            token: строка для проверки

        Returns:
            True если токен является числом, иначе False
        """
        try:
            float(token)
            return True
        except ValueError:
            return False

    def shunting_yard(self, expression: str) -> list:
        """
        Преобразует инфиксное выражение в обратную польскую нотацию
        используя алгоритм сортировочной станции (Shunting Yard)

        Args:
            expression: математическое выражение в инфиксной нотации

        Returns:
            Список токенов в RPN
        """
        tokens = self.tokenize(expression)
        output = []
        operator_stack = []

        for token in tokens:
            if self.is_number(token):
                output.append(token)
            elif token in self.operators:
                while (operator_stack and
                       operator_stack[-1] != '(' and
                       self._should_pop_operator(token, operator_stack[-1])):
                    output.append(operator_stack.pop())
                operator_stack.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                while operator_stack and operator_stack[-1] != '(':
                    output.append(operator_stack.pop())
                if operator_stack and operator_stack[-1] == '(':
                    operator_stack.pop()
                else:
                    raise ValueError("Несбалансированные скобки")

        while operator_stack:
            if operator_stack[-1] in '()':
                raise ValueError("Несбалансированные скобки")
            output.append(operator_stack.pop())

        return output

    def _should_pop_operator(self, current_op: str, stack_top: str) -> bool:
        """
        Определяет, нужно ли выталкивать оператор из стека

        Args:
            current_op: текущий оператор
            stack_top: оператор на вершине стека

        Returns:
            True если нужно вытолкнуть оператор из стека
        """
        if stack_top not in self.operators:
            return False

        current_prec = self.operators[current_op]['precedence']
        stack_prec = self.operators[stack_top]['precedence']
        current_assoc = self.operators[current_op]['associativity']

        return (stack_prec > current_prec or
                (stack_prec == current_prec and current_assoc == 'left'))

    def evaluate_rpn(self, rpn_expression: list) -> float:
        """
        Вычисляет значение выражения в обратной польской нотации

        Args:
            rpn_expression: список токенов в RPN

        Returns:
            Результат вычисления
        """
        stack = []

        for token in rpn_expression:
            if self.is_number(token):
                stack.append(float(token))
            elif token in self.operators:
                if len(stack) < 2:
                    raise ValueError("Недостаточно операндов для оператора")

                op2 = stack.pop()
                op1 = stack.pop()

                if token == '/' and op2 == 0:
                    raise ValueError("Деление на ноль")

                result = self.operators[token]['function'](op1, op2)
                stack.append(result)
            else:
                raise ValueError(f"Неизвестный токен: {token}")

        if len(stack) != 1:
            raise ValueError("Некорректное выражение")

        return stack[0]

    def calculate(self, expression: str) -> float:
        """
        Вычисляет значение математического выражения

        Args:
            expression: математическое выражение в инфиксной нотации

        Returns:
            Результат вычисления
        """
        # Удаляем пробелы
        expression = expression.replace(' ', '')

        if not expression:
            raise ValueError("Пустое выражение")

        rpn = self.shunting_yard(expression)
        return self.evaluate_rpn(rpn)


def main():
    """Основная функция для интерактивного использования калькулятора"""
    calculator = RPNCalculator()

    print("Калькулятор с обратной польской нотацией")
    print("Поддерживаемые операции: +, -, *, /, ^, скобки")
    print("Введите 'quit' для выхода")

    while True:
        try:
            expression = input("\nВведите выражение: ").strip()

            if expression.lower() in ['quit', 'exit', 'q']:
                break

            if not expression:
                continue

            result = calculator.calculate(expression)
            rpn = calculator.shunting_yard(expression)

            print(f"RPN: {' '.join(rpn)}")
            print(f"Результат: {result}")

        except ValueError as e:
            print(f"Ошибка: {e}")
        except (KeyboardInterrupt, EOFError):
            print("\nВыход из программы")
            break
        except Exception as e:  # pylint: disable=broad-except
            print(f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    main()

