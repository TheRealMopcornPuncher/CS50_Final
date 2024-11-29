from flask import Flask, render_template, redirect, request
from helpers.keyword_extractor import KeywordExtractor
from helpers.combine_wordlist import combine_wordlist
from helpers.gen_hash import gen_hash
from helpers.most_repeated import most_repeated_word
from helpers.article_retrieve import process_news
import sqlite3

app = Flask(__name__)

# Define the pages
pages = ["Home", "Past", "Description"]

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('summaries.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return redirect("/home")

@app.route("/home", methods=["GET", "POST"])
def home():
    currentPage = "home"
    if request.method == "POST":
        query = request.form.get('searchTopic')

        # Check if the query is not empty
        if query:
            # Call the process_news function which handles fetching articles, summarizing them, and saving the summary
            summary = process_news(query)
            
            # If a summary is generated, save it to the database (already done inside process_news)
            if summary:
                # Redirect to the past page to view the summary
                return redirect("/past")

    return render_template("Home.html", pages=pages, currentPage=currentPage)

@app.route("/past", methods=["GET", "POST"])
def past():
    currentPage = "past"
    # Fetch all past summaries from the database
    conn = get_db_connection()
    summaries = conn.execute('SELECT * FROM summaries ORDER BY date_created DESC').fetchall()
    conn.close()
    
    return render_template("Past.html", pages=pages, currentPage=currentPage, summaries=summaries)

@app.route("/description", methods=["GET", "POST"])
def description():
    currentPage = "description"
    return render_template("Description.html", pages=pages, currentPage=currentPage)

# Save the generated summary to the database
def save_summary_to_db(query, summary):
    conn = get_db_connection()
    conn.execute('INSERT INTO summaries (query, summary) VALUES (?, ?)', (query, summary))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    app.run(debug=True)
