# cs50x-final-project
## MANGA GPA 
#### Video Demo:  <https://youtu.be/QIO0UcUFU2E>
manga gpa is a web application dedicated to calculate the gpa of mansoura university engineering students with some usefull funcionality, this web application is created by flask framework and with the use of some other programming languages such as javascript, SQLite3,css,html 

## app.py
app.py is the main python file which contains the back-end of the web application, first we import the necessary librarys 
```python
import os
import re
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required
```

## app.py functions
### in app.py we have a function for each html page.

## login
first we check if the username an password provided are correct when the method is POST, then creating a session and redirecting the user to the index page.

```python
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
```
### login.html
the login page has a simple form for the user to input his username and password
```html
<form action="/login" method="post">
        <div class="mb-3">
            <input autocomplete="off" autofocus class="form-control mx-auto w-auto" id="username" name="username" placeholder="Username" type="text">
        </div>
        <div class="mb-3">
            <input class="form-control mx-auto w-auto" id="password" name="password" placeholder="Password" type="password">
        </div>
        <button class="btn btn-success" type="submit">Log In</button>
    </form>
```

## register
the register function is similar to the login function, it takes the username ,password and password confirmation then check using a regex if the password is at least 8 character and has at least one letter, if all conditions are met, the input is inserted in the data-base, a session is created and you get redirecetd to the index page

```python
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
```
### register.html
the register page has a simple form for the uder to input his username, password and password confirmation
```html
    <form action="/register" method="post">
        <div class="mb-3">
            <input autocomplete="off" autofocus class="form-control mx-auto w-auto" id="username" name="username" placeholder="Username" type="text">
        </div>
        <div class="mb-3">
            <input class="form-control mx-auto w-auto" name="password" placeholder="Password" type="password">
        </div>
        <div class="mb-3">
            <input class="form-control mx-auto w-auto" name="confirmation" placeholder="Confirm password" type="password">
        </div>
        <div>
            <button class="btn btn-success" type="submit">Register</button>
        </div>
    </form>
```
## Add
in the add page if it is accessed via GET we render the add.html file that has a form for you to add your subject, if the method is POST that means that the user submitted the form, then the add function check all the possible errors returning an apology if there is any errors, if no errors, the subject is inserted into the data base.

```python
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
```
### add.html
the login page has a simple form for the user to add subject(s), you can add more than one subject and you won't get redirected to the index page unless you click "finish"
```html
    <form action="/add" method="post">
        <div class="mb-3">
            <input autocomplete="off" autofocus class="form-control mx-auto w-auto"  name="name" placeholder="Subject Name" type="text">
            <input autocomplete="off" autofocus class="form-control mx-auto w-auto"  name="hours" placeholder="Credit Hours" type="number" min="1" max="6">
            <input autocomplete="off" autofocus class="form-control mx-auto w-auto" id="percent" name="percent" placeholder="Score" type="number" min="1" max="100">
            <input autocomplete="off" autofocus class="form-control mx-auto w-auto" readonly id="gpa" name="gpa" placeholder="gpa" type="number" step="0.01" min="0" max="4" >
            <button class="btn btn-success" type="submit">Add</button>
        </div>
        
    </form>
    <div class="mb-3">
        <a href='/'>
            <button class="btn btn-success" type="submit">Finish</button>
        </a>
```
### gpa input change depending on the score
to make it easier for the user the add.html has some javascript that makes the gpa change depending on the score at constant time
```html
    <script>
        let input = document.querySelector('#percent');
        input.addEventListener('input', async function() {
            let shows = input.value;
            if(input.value > 100){
                shows = 0.0
            }
            else if (input.value >= 93){
                shows = 4.0
            }
            else if(input.value >= 89){
                shows = 3.7
            }
            else if(input.value >= 84){
                shows = 3.3
            }
            else if(input.value >= 80){
                shows = 3.0
            }
            else if(input.value >= 76){
                shows = 2.7
            }
            else if(input.value >= 73){
                shows = 2.3
            }
            else if(input.value >= 70){
                shows = 2.0
            }
            else if(input.value >= 67){
                shows = 1.7
            }
            else if(input.value >= 64){
                shows = 1.3
            }
            else if(input.value >= 60){
                shows = 1.0
            }
            else{
                shows = 0.0
            }

            document.querySelector("#gpa").value = shows;
        });
    </script>
```
## Index 
Index function takes all the data from the data-base then calculates the gpa and pass all of that data to index.html to display them

```python
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
```
### index.html
the index page is simply a table with a roe for each subject, we use a jinja loop to make the table grow and shrink depending on the number of subjects
```html
<div class="container text-center">
    <div class="custyle">
        <table class="table table-striped custab">
            <thead>

                <tr>
                    <th class="text-end">Total GPA</th>
                    <th class="text-end">Total Percentage</th>
                    <th class="text-end">Total Credit Hours</th>
                </tr>
            </thead>
            <tr>
                <td class="text-end">{{ total_gpa }}</td>
                <td class="text-end">{{ total_percent }}</td>
                {% if total_hours == 1000 %}
                <td class="text-end">0</td>
                {% else %}
                <td class="text-end">{{ total_hours }}</td>
                {% endif %}
            </tr>
        </table>
    </div>
</div>

<div class="container text-center">
    <div class="custyle">
        <table class="table table-striped custab">
            <thead>

                <tr>
                    <th class="text-end">Subject</th>
                    <th class="text-end">Credit Hours</th>
                    <th class="text-end">Score</th>
                    <th class="text-end">Grade</th>
                    <th class="text-end">GPA</th>
                    <th class="text-center">Action</th>
                </tr>
            </thead>

            {% for subject in subjects %}
            <tr>
                <td class="text-end">{{ subject.name }}</td>
                <td class="text-end">{{ subject.hours }}</td>
                <td class="text-end">{{ subject.percent }}</td>
                <td class="text-end">{{ subject.grade }}</td>
                <td class="text-end">{{ subject.gpa }}</td>
                <!-- <td class="text-center"><a class="btn icon-btn btn-success" onclick="document.getElementById('id02').style.display='block'"><span class="glyphicon btn-glyphicon glyphicon-pencil img-circle text-success"></span>Edit</a>
                                        <a class="btn icon-btn btn-danger" onclick="document.getElementById('id01').style.display='block'" ><span class="glyphicon btn-glyphicon glyphicon-trash img-circle text-danger"></span>Delete</a>
                </td> -->
                <td class="list-inline-item">
                    <button class="btn btn-success btn-sm rounded-0" onclick="document.getElementById('id02').style.display='block'" type="button" data-toggle="tooltip" data-placement="top" title="Edit"><i class="fa fa-edit"></i></button>
                
                    <button class="btn btn-danger btn-sm rounded-0" onclick="document.getElementById('id01').style.display='block'" type="button" data-toggle="tooltip" data-placement="top" title="Delete"><i class="fa fa-trash"></i></button>
                </td>
            </tr>
    </div>
```
## Modal
to make it easier for the user to modify his subject we added a delete and edit buttons for each subject ib the index page, when the user click on any of them a modal pops up so that he can confirm the delete or add the edit input 

```python
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
```
### modal.html
there are two modals, one for editing and one for deleting, the edit modal allows the user to modify the data of the subject selected and the delete modal asks the user if he is sure that he wants to delete the subject or not
```html
    <!-- modal for edit button -->
    <div id="id02" class="modal">
        <span onclick="document.getElementById('id02').style.display='none'" class="close" title="Close Modal">×</span>
        <div class="modal-dialog modal-dialog-centered" role="document">
            <div class="modal-content">
                <form action="/modal" method="post">
                    <div class="modal-header">
                        <div class="modal-title">
                            <h1>Edit Subject</h1>
                        </div>
                    </div>
                    <div class="modal-body">
                        <div class="mb-3">
                            <input autocomplete="off" autofocus class="form-control mx-auto w-auto"  name="name" placeholder="Subject Name" type="text">
                            <input autocomplete="off" autofocus class="form-control mx-auto w-auto"  name="hours" placeholder="Credit Hours" type="number" min="1" max="6">
                            <input autocomplete="off" autofocus class="form-control mx-auto w-auto"  id="percent" name="percent" placeholder="Score" type="number" min="1" max="100">
                            <input autocomplete="off" autofocus class="form-control mx-auto w-auto"  readonly id="gpa" name="gpa" placeholder="gpa" type="number" step="0.01" min="0" max="4" >
                        </div>
                    </div>
                    <div class="modal-footer">
                        <div class="clearfix">
                            <button type="button" class="btn btn-secondary" data-dismiss="modal"
                                onclick="document.getElementById('id02').style.display='none'"
                                class="cancelbtn">Cancel</button>
                            <button type="submit" name="edit_id" value={{ subject.id }} type="button"
                                class="btn btn-success" onclick="document.getElementById('id02').style.display='none'"
                                class="deletebtn">Edit</button>
                        </div>
                    </div>
                </form>
            </div>
        </div>
    </div>
```
# about.html
the about page uses the Tango Crome extention to make a workflow that helps users use the web application


# style
in the style aspect of the web application we rely mainly on bootstrap and we add some touches using styless.css 

# data base
we use a sqlite3 data dase that contains two tables: users table and subject table, the user table has the username and the hashed password, the subject table has the name of the subject, hours, percent aka score, gpa and a foreign key that refference the id of the users table

# helpers.py
it has to functions : apology and login_required, the apology function makes an error photo with the message and the error code , and the login_required function -as the name implies- makes sure that the user is logged in.