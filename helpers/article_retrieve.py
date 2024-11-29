from datetime import datetime, timedelta, timezone
import requests
from transformers import pipeline
import sqlite3

# Global API Key
API_KEY = "c3379e1e7c3b49db8ea3f8971ba0c2f2"

# Calculate Date Range for the Past Week
today = datetime.now(timezone.utc).date()
one_week_ago = today - timedelta(days=7)
start_date = one_week_ago.strftime("%Y-%m-%d")
end_date = today.strftime("%Y-%m-%d")

# Initialize the summarizer
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-6-6")

def fetch_articles(query, start_date, end_date, api_key=API_KEY):
    """
    Fetch the top 10 most viewed articles from NewsAPI based on a query word.
    """
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "from": start_date,
        "to": end_date,
        "sortBy": "popularity",
        "pageSize": 10,  # Top 10 articles
        "apiKey": api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        articles = response.json().get("articles", [])
        return articles
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return []


def combine_articles(articles):
    """
    Combine the content, description, and title of all articles into a single string for summarization.
    """
    combined_text = ""
    for article in articles:
        title = article.get("title", "")
        description = article.get("description", "")
        content = article.get("content", "")
        
        combined_text += f"{title} {description} {content} "
    
    return combined_text


def split_into_chunks(text, max_tokens=1024):
    """
    Split text into chunks that are within the token limit of the model.
    """
    words = text.split()
    chunks = []
    chunk = []

    # Track token count as we add words
    for word in words:
        chunk.append(word)
        # Approximate token length: consider 1 word ≈ 1 token
        if len(" ".join(chunk)) > max_tokens:
            chunks.append(" ".join(chunk[:-1]))  # Add the chunk, but exclude the last word
            chunk = [word]  # Start a new chunk

    if chunk:
        chunks.append(" ".join(chunk))  # Add the last chunk if any
    
    return chunks


def summarize_articles(text):
    """
    Summarize the combined article text using DistilBART, splitting it into smaller chunks if necessary.
    """
    # Split the article into chunks
    chunks = split_into_chunks(text)
    
    summaries = []
    for chunk in chunks:
        # Dynamically adjust max_length based on input length but within reasonable bounds
        input_length = len(chunk.split())
        
        # Ensure max_length is at least 8 and at most 150
        max_length = min(max(input_length, 8), 150)
        
        # Adjust min_length to be smaller than max_length, with a lower bound of 8
        min_length = min(max(max_length // 2, 8), 50)
        
        # Summarize the chunk
        summary = summarizer(chunk, max_length=max_length, min_length=min_length, do_sample=False)
        summaries.append(summary[0]['summary_text'])
    
    # Combine all the summaries into one
    full_summary = " ".join(summaries)
    return full_summary


def create_database():
    """
    Create the summaries.db database and the summaries table if it doesn't exist.
    """
    conn = sqlite3.connect("summaries.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS "summaries" (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        summary TEXT NOT NULL,
        query TEXT NOT NULL,
        date_created DATE DEFAULT CURRENT_DATE
    )
    """)
    conn.commit()
    conn.close()


def save_summary(summary, query):
    """
    Save a generated summary into the summaries.db database along with the query.
    """
    conn = sqlite3.connect("summaries.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO summaries (summary, query) VALUES (?, ?)", (summary, query))
    conn.commit()
    conn.close()


def process_news(query):
    """
    Complete process to fetch articles, summarize them, and save the summary to the database.
    """
    # Fetch articles
    articles = fetch_articles(query, start_date, end_date)
    if not articles:
        print("No articles found.")
        return None  # Return None if no articles are found

    # Combine article content
    articles_text = combine_articles(articles)

    # Summarize the content
    summary = summarize_articles(articles_text)
    print(f"Summary:\n{summary}")

    # Save summary to database
    create_database()  # Ensure the database and table exist
    save_summary(summary, query)
    print("Summary saved to database.")
    
    return summary  # Return the summary for further use if needed
