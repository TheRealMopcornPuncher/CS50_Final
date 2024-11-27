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
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Get token embeddings
        token_embeddings = outputs.last_hidden_state[0]

        # Compute sentence embedding
        sentence_embedding = token_embeddings.mean(dim=0, keepdim=True)

        # Compute cosine similarity between sentence and token embeddings
        similarities = cosine_similarity(
            token_embeddings.numpy(), sentence_embedding.numpy()
        ).flatten()

        # Map token IDs to words
        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])

        # Sort tokens by similarity and filter out stopwords and special tokens
        token_scores = sorted(
            [(tokens[i], score) for i, score in enumerate(similarities)],
            key=lambda x: x[1],
            reverse=True,
        )
        keywords = []
        for token, _ in token_scores:
            token = token.replace("##", "")  # Merge subwords
            if (
                token not in self.stopwords  # Remove stopwords
                and token not in self.tokenizer.all_special_tokens  # Remove special tokens
                and token not in string.punctuation  # Remove punctuation
                and len(token) > 2  # Remove very short tokens
            ):
                keywords.append(token)
            if len(keywords) == top_n:
                break

        return keywords
