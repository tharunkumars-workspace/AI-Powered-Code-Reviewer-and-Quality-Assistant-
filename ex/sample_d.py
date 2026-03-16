# sample_d.py

def factorial(n):
    """
    Compute factorial of a number.

    Args:
        n (int): Non-negative integer.

    Returns:
        int: Factorial of n.
    """
    if n == 0:
        return 1
    return n * factorial(n - 1)


class Printer:
    def display(self, message):
        """
        Display a message.

        Args:
            message (str): Message to print.
        """
        print(message)