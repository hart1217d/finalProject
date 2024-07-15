import os

import sqlite3
# need a module that will serve to update SQL databases (from cs50 import SQL)
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

con = sqlite3.connect('C:/Users/Hart/OneDrive/Documents/Coding/CS50/FinalProject/tsranker.db', check_same_thread=False)
cur = con.cursor()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html")
        
        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html")
        
        # Query database for username
        rows = cur.execute(
            "SELECT * FROM users WHERE username = ?", [request.form.get("username")] 
        )

        # Ensure username exists and password is correct
        if rows.fetchone() is None or not check_password_hash(
            rows[2], request.form.get("password")
        ):
            return render_template("login.html")
        
        # Remember which user has logged in
        session["user_id"] = id

        # Redirect user to home page
        return redirect("/")
    
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Change User's Password"""
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username or not password or not confirmation:
            return render_template("register.html")
        
        if not password == confirmation:
            return render_template("register.html")
        
        try:
            hash = generate_password_hash(password, salt_length=16)
            data = (username, hash)
            cur.execute("INSERT INTO users (username, hash) VALUES (?, ?)", data)
            con.commit()
            return render_template("login.html")
        except ValueError:
            return render_template("register.html")
        
    else:
        return render_template("register.html")