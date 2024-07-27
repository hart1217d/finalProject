import os

import sqlite3
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
        cur.execute(
            "SELECT * FROM users WHERE username = ?", [request.form.get("username")] 
        )
        user = cur.fetchone()

        # Ensure username exists and password is correct
        if user and check_password_hash(user[2], request.form.get("password")):
            session["user_id"] = user[0]
            return redirect("/")
        else:
            return render_template("login.html")
    
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/setup", methods=["GET", "POST"])
def setup():
    if request.method == "POST":
        user_id = str(session["user_id"])
        system_info = ()

        # Find or create system table
        while not system_info:
            cur.execute("SELECT system_name, ready, modified FROM systems WHERE user_id = ?", user_id)
            system_info = cur.fetchone()
            if not system_info:
                system_name = "system" + user_id
                cur.execute("INSERT INTO systems (user_id, system_name) VALUES (?, ?)", (user_id, system_name))
                cur.execute(
                    """
                    CREATE TABLE ? (
                    attribute_name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    min INTEGER NOT NULL DEFAULT(0),
                    max INTEGER NOT NULL DEFAULT(0),
                    length_depend BOOLEAN DEFAULT(FALSE)
                    )
                    """
                    , system_name)
        
        if not request.form.get("type") or not request.form.get("attribute_name"):
            return render_template("setup.html")
        
        if request.form.get("type") == "yes/no":
            attribute_name = request.form.get("attribute_name")
            entries = (attribute_name, "yes/no", 0, 1, False)
            if request.form.get("length_depend"):
                entries[4] = True
            cur.execute("INSERT INTO ? (attribute_name, type, min, max, length_depend) VALUES (?, ?, ?, ?, ?)", entries)
        
        elif request.form.get("type") == "scale":
            if not request.form.get("scale"):
                return render_template("setup.html")
            attribute_name = request.form.get("attribute_name")
            scale_min = 0
            if request.form.get("scale") == "LoMeHi":
                scale_max = 3
            elif request.form.get("scale") == "fiveScale":
                scale_max = 5
            elif request.form.get("scale") == "tenScale":
                scale_max = 10
            entries = (attribute_name, "scale", scale_min, scale_max, False)
            if request.form.get("length_depend"):
                entries[4] = True
            cur.execute("INSERT INTO ? (attribute_name, type, min, max, length_depend) VALUES (?, ?, ?, ?, ?)", entries)
        
        elif request.form.get("type") == "percent":
            attribute_name = request.form.get("attribute_name")
            entries = (attribute_name, "percent", 0, 1, False)
            if request.form.get("length_depend"):
                entries[4] = True
            cur.execute("INSERT INTO ? (attribute_name, type, min, max, length_depend) VALUES (?, ?, ?, ?, ?)", entries)
        
        elif request.form.get("type") == "count":
            attribute_name = request.form.get("attribute_name")
            entries = (attribute_name, "count", 0, 1000, False)
            if request.form.get("length_depend"):
                entries[4] = True
            cur.execute("INSERT INTO ? (attribute_name, type, min, max, length_depend) VALUES (?, ?, ?, ?, ?)", entries)
        
        return render_template("setup.html")
    
    else:
        user_id = str(session["user_id"])
        cur.execute("SELECT system_name, ready, modified FROM systems WHERE user_id = ?", user_id)
        system_info = cur.fetchone()
        if not system_info:
            return render_template("setup.html")
        else:
            system = cur.execute("SELECT * FROM ? ", system_info[0])
            ready = system_info[1]
            return render_template("setup.html", system=system, ready=ready)

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