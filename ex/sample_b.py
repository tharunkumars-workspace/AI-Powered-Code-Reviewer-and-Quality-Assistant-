# sample_b.py

def generator_example(n):
    """
    Generate numbers from 0 to n-1.

    Args:
        n (int): Upper limit.

    Yields:
        int: Next number in sequence.
    """
    for i in range(n):
        yield i


def raises_example(x):
    """
    Multiply input by 2 if positive.

    Args:
        x (int): Input number.

    Returns:
        int: Doubled value.

    Raises:
        ValueError: If x is negative.
    """
    if x < 0:
        raise ValueError("negative")
    return x * 2