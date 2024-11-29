# combine_wordlist.py

def combine_wordlist(*word_lists):
    """
    Combines multiple word lists into a single list.

    Parameters:
        *word_lists (list of lists): Lists of words to be combined.

    Returns:
        list: A single list containing all the words.
    """
    combined_list = []

    for word_list in word_lists:
        if isinstance(word_list, list):
            combined_list.extend(word_list)
        else:
            raise ValueError("Each input must be a list of words.")

    return combined_list
