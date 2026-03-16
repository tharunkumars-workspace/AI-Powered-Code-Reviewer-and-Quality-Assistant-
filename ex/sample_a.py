# sample_a.py

def calculate_average(numbers):
    """
    Calculate the average of a list of numbers.

    Args:
        numbers (list): List of numeric values.

    Returns:
        float: Average of the numbers. Returns 0 if list is empty.
    """
    total = 0
    for n in numbers:
        total += n
    if len(numbers) == 0:
        return 0
    return total / len(numbers)


def add(a: int, b: int) -> int:
    """
    Add two integer values.

    Args:
        a (int): First integer.
        b (int): Second integer.

    Returns:
        int: Sum of a and b.
    """
    return a + b


class Processor:
    def process(self, data):
        for item in data:
            if item is None:
                continue
            print(item)