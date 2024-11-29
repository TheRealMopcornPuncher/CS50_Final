# most_repeated.py

def most_repeated_word(words):
    """
    Finds the most repeated word in a given list of words.

    Parameters:
        words (list): A list of words extracted from articles.

    Returns:
        tuple: The most repeated word and its count.
    """
    if not words:
        return None, 0  # Handle empty input gracefully

    word_count = {}

    # Populate hash map with word frequencies
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1

    # Identify the most repeated word
    most_frequent_word = max(word_count, key=word_count.get)
    return most_frequent_word, word_count[most_frequent_word]
