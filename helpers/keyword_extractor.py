import nltk
from nltk.corpus import stopwords
from transformers import BertTokenizer, BertModel
from sklearn.metrics.pairwise import cosine_similarity
import torch
import string

class KeywordExtractor:
    def __init__(self):
        # Ensure stopwords are downloaded
        try:
            self.stopwords = set(stopwords.words("english"))
        except LookupError:
            nltk.download("stopwords")
            self.stopwords = set(stopwords.words("english"))

        # Load BERT model and tokenizer
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.model = BertModel.from_pretrained("bert-base-uncased")

    def extract_keywords(self, text, top_n=5):
        """
        Extracts keywords from the given text using BERT embeddings and cosine similarity.

        Args:
            text (str): The input text to extract keywords from.
            top_n (int): The number of top keywords to return.

        Returns:
            list: A list of extracted keywords.
        """
        # Tokenize and encode the text
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)

        if "input_ids" not in inputs or len(inputs["input_ids"]) == 0:
            raise ValueError("Tokenization failed. Please check the input text.")

        with torch.no_grad():
            outputs = self.model(**inputs)

        # Get token embeddings
        token_embeddings = outputs.last_hidden_state[0]

        input_ids = inputs["input_ids"][0]
        if len(input_ids) != len(token_embeddings):
            raise ValueError("Mismatch between tokens and embeddings.")

        # Compute sentence embedding
        sentence_embedding = token_embeddings.mean(dim=0, keepdim=True)

        # Compute cosine similarity between sentence and token embeddings
        similarities = cosine_similarity(
            token_embeddings.numpy(), sentence_embedding.numpy()
        ).flatten()

        # Map token IDs to words
        tokens = self.tokenizer.convert_ids_to_tokens(input_ids)

        # Reconstruct words while maintaining alignment
        words = []
        indices = []  # Track the original indices of reconstructed words
        current_word = ""
        for idx, token in enumerate(tokens):
            if token.startswith("##"):
                # Merge subword with the current word
                current_word += token[2:]
            else:
                # Append the completed word and start a new one
                if current_word:
                    words.append(current_word)
                    indices.append(idx - 1)  # Record the index of the completed word
                current_word = token

        if current_word:  # Add the last word if any
            words.append(current_word)
            indices.append(len(tokens) - 1)

        # Filter similarities to match the reconstructed words
        filtered_similarities = [similarities[i] for i in indices]

        # Sort words by similarity
        token_scores = sorted(
            [(words[i], score) for i, score in enumerate(filtered_similarities)],
            key=lambda x: x[1],
            reverse=True,
        )

        # Extract top keywords
        keywords = []
        seen = set()
        for word, _ in token_scores:
            word = word.lower()
            if (
                word not in self.stopwords
                and word not in string.punctuation
                and len(word) > 2
                and word not in seen
            ):
                keywords.append(word)
                seen.add(word)

            if len(keywords) == top_n:
                break

        return keywords
