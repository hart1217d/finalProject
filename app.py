import os

# need a module that will serve to update SQL databases (from cs50 import SQL)
from flask import Flask, flash, redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required

app = Flask(__name__)

@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    "show history"
    return render_template("index.html")