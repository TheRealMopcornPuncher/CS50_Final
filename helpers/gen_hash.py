# gen_hash.py

def gen_hash(words):
    """
    Generates a hash map for word frequencies.

    Parameters:
        words (list): A list of words.

    Returns:
        dict: A dictionary with words as keys and their frequencies as values.
    """
    if not isinstance(words, list):
        raise ValueError("Input must be a list of words.")

    word_count = {}

    # Populate the hash map with word frequencies
    for word in words:
        word_count[word] = word_count.get(word, 0) + 1

    return word_count
