# sample_e.py

def reverse_string(text):
    """
    Reverse a given string.

    Args:
        text (str): Input string.

    Returns:
        str: Reversed string.
    """
    return text[::-1]


def count_vowels(text):
    """
    Count number of vowels in a string.

    Args:
        text (str): Input string.

    Returns:
        int: Number of vowels.
    """
    vowels = "aeiouAEIOU"
    return sum(1 for char in text if char in vowels)