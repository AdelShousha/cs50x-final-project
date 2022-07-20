import os
import re
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://")
db = SQL(postgres://zsrodnehaxbeqh:10a8e7652844120da38126fe443744c2af0ea58c855e86a71802024c4c251965@ec2-52-204-157-26.compute-1.amazonaws.com:5432/da1nr92hbbh934)


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
    # select all the data from the subject table
    subjects = db.execute(
        "SELECT id, name, hours, percent, gpa FROM subject WHERE users_id = ? ", session["user_id"])    
    total_hours = db.execute(
        "SELECT SUM(hours) FROM subject WHERE users_id = ?", session["user_id"])
    if total_hours[0]["SUM(hours)"] == None:
        total_hours[0]["SUM(hours)"] = 1000
    # automatically assigning the grade to the subject depending on the score
    for subject in subjects:
        if int(subject["percent"]) >= 97:
            subject["grade"] = "A+"
        elif int(subject["percent"]) >= 93:
            subject["grade"] = "A"    
        elif int(subject["percent"]) >= 89:
            subject["grade"] = "A-"
        elif int(subject["percent"]) >= 84:
            subject["grade"] = "B+"
        elif int(subject["percent"]) >= 80:
            subject["grade"] = "B"
        elif int(subject["percent"]) >= 76:
            subject["grade"] = "B-"
        elif int(subject["percent"]) >= 73:
            subject["grade"] = "C+"
        elif int(subject["percent"]) >= 70:
            subject["grade"] = "C"
        elif int(subject["percent"]) >= 67:
            subject["grade"] = "C-"
        elif int(subject["percent"]) >= 64:
            subject["grade"] = "D+"
        elif int(subject["percent"]) >= 60:
            subject["grade"] = "D"
        else:
            subject["grade"] = "F"    
    # calculating the total gpa
    total_gpa = 0
    for subject in subjects:
        total_gpa = total_gpa + float(subject["gpa"]) * float(subject["hours"])
    
    # calculating the total gpa
    total_percent = 0
    for subject in subjects:
        total_percent = total_percent + float(subject["percent"]) * float(subject["hours"])

    return render_template("index.html", subjects=subjects, total_hours=total_hours[0]["SUM(hours)"], total_gpa=round(total_gpa/int(total_hours[0]["SUM(hours)"]), 2),
    total_percent=round(total_percent/int(total_hours[0]["SUM(hours)"]), 2))

@app.route("/modal", methods=["POST"])
@login_required
def modal():
    
    # if the add button is clicked passing the content of the form to the database 
    edit_id = request.form.get("edit_id")
    if edit_id:
        name = request.form.get("name")
        hours = request.form.get("hours")
        percent = request.form.get("percent")
        gpa = request.form.get("gpa")

        # check if the input is valid
        errors = [{"variable": name, "error": "must type a subject name"},
                    {"variable": hours, "error": "must type the credit hours"},
                    {"variable": percent, "error": "must type the percentage"},
                    {"variable": gpa, "error": "must type the gpa"}]
        # looping over all the dicts making sure that the user entered all the required info
        for error in errors:
            if not error["variable"]:
                return apology(error["error"])

        # check if the number is fraction or less than 0
        if not hours.isdigit() or not percent.isdigit():
            return apology("invalid hours or percentage")
        if int(hours) < 0 or int(percent) < 1 or float(gpa) < 0 :
            return apology("numbers must be positive")
        if int(hours) > 6 or int(percent) > 100 or float(gpa) > 4 :
            return apology("out of range")
        # update the database
        db.execute("UPDATE subject SET name = ?, hours = ?, percent = ?, gpa = ? WHERE id = ?", name, hours, percent, gpa, edit_id)

    # if the delete button is clicked delete the subject from the database
    delete_id = request.form.get("delete_id")
    if delete_id:
        db.execute("DELETE FROM subject WHERE id = ? ", delete_id)
    
    return redirect("/")


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "GET":
        return render_template("add.html")
    else:
        # get the input of the user
        name = request.form.get("name")
        hours = request.form.get("hours")
        percent = request.form.get("percent")
        gpa = request.form.get("gpa")

        # check if the input is valid
        errors = [{"variable": name, "error": "must type a subject name"},
                  {"variable": hours, "error": "must type the credit hours"},
                  {"variable": percent, "error": "must type the percentage"},
                  {"variable": gpa, "error": "must type the gpa"}]
        # looping over all the dicts making sure that the user entered all the required info
        for error in errors:
            if not error["variable"]:
                return apology(error["error"])

        # check if the number is fraction or less than 0
        if not hours.isdigit() or not percent.isdigit():
            return apology("invalid hours or percentage")
        if int(hours) < 0 or int(percent) < 1 or float(gpa) < 0 :
            return apology("numbers must be positive")
        if int(hours) > 6 or int(percent) > 100 or float(gpa) > 4 :
            return apology("out of range")
        
            # insert the new subject in the database
        db.execute("INSERT INTO subject (name, hours, percent, gpa, users_id) VALUES(?, ?, ?, ?, ?)", name, hours, percent, gpa, session["user_id"])
            

    return redirect("/add")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
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
    # when accessing the page via GET, render the register page
    if request.method == "GET":
        return render_template("register.html")

    else:  # accessing via POST
        # putting the input that the user entered in variables
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # making a user list that has all the usernames in the database
        users = [sub['username'] for sub in db.execute("SELECT username FROM users")]

        # making a list of dicts which has a dict for every error
        errors = [{"variable": username, "error": "must type a username"},
                  {"variable": password, "error": "must type a password"},
                  {"variable": confirmation, "error": "must type a the confirmation password"}]
        # looping over all the dicts making sure that the user entered all the required info
        for error in errors:
            if not error["variable"]:
                return apology(error["error"])

        # regex to make the password at least 8 char and has one letter
        regex = "^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
        result = re.match(regex, password)
        if not result:
            return apology("Minimum 8 characters and at least one letter and one number")

        # making sure that the password and the confirmation are the same
        if password != confirmation:
            return apology("passwords don't match")
        # checking to see if the username already exists
        if username in users:
            return apology("username already exists")

        # hashing the password to make it secure
        hash_pass = generate_password_hash(password)

        # inserting the username and the hashed password into the database
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash_pass)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        # logging user in
        session["user_id"] = rows[0]["id"]
    return redirect("/")

@app.route("/about")
@login_required
def about():
    return render_template("about.html")