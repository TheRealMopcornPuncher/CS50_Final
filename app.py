from flask import Flask, flash, jsonify, redirect, render_template, request, session

app = Flask(__name__)

@app.route("/")
def index():
    pages = ["Home", "Old", "New"]
    currentPage = "Home"
    return render_template("index.html", pages=pages, currentPage=currentPage)