def add(a, b):
    """
    Adds two numbers together.

    Args:
        a (int or float): The first number to add.
        b (int or float): The second number to add.

    Returns:
        int or float: The sum of a and b.

    Raises:
        TypeError: If a or b are not numbers.
    """
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b): 
    """
    Calculates the product of two numbers.

    - Parameters:
      - a (int or float): The first number to multiply.
      - b (int or float): The second number to multiply.

    - Returns:
      - result (int or float): The product of a and b.
    """
    return a * b  # This line is intentionally made very very very very very very very very very long to trigger line length issue 2.3i # pyright: ignore[reportUndefinedVariable]