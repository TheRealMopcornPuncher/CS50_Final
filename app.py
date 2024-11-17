from flask import Flask, render_template, redirect
import sqlite3

conn = sqlite3.connect('summaries.db')

app = Flask(__name__)

# Define the pages
pages = ["Home", "Past", "Description"]

@app.route("/")
def index():
    return redirect("/home")

@app.route("/home", methods=["GET", "POST"])
def home():
    currentPage = "home"  # Store in lowercase for use in links
    return render_template("Home.html", pages=pages, currentPage=currentPage)

@app.route("/past", methods=["GET", "POST"])
def past():
    currentPage = "past"  # Store in lowercase for use in links
    return render_template("Past.html", pages=pages, currentPage=currentPage)

@app.route("/description", methods=["GET", "POST"])
def description():
    currentPage = "description"  # Store in lowercase for use in links
    return render_template("Description.html", pages=pages, currentPage=currentPage)
