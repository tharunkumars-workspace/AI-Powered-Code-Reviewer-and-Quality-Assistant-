def add(a, b):
    """
    Add two numbers and return the result.
    """
    return a + b


def subtract(a, b):
    """
    Subtract second number from first number.
    """
    return a - b


def multiply(a, b):
    """
    Multiply two numbers.
    """
    result = 0
    for _ in range(b):
        result += a
    return result