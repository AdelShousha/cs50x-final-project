import os

import re
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


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
    # select unique list of dicts of all symbols and names
    stocks = db.execute(
        "SELECT stock_symbol, stock_name FROM purchase WHERE users_id = ? GROUP BY stock_symbol", session["user_id"])
    # print(stocks)
    #[{'stock_symbol': 'G', 'stock_name': 'Genpact Ltd'}, {'stock_symbol': 'NFLX', 'stock_name': 'Netflix Inc.'}]

    for stock in stocks:
        # select the total number of shares of each stock

        # get buy and sell shares
        buy_shares = db.execute("SELECT SUM(shares) FROM purchase WHERE (users_id = ?) AND (action = ?) AND (stock_symbol = ?)",
                                session["user_id"], "buy", stock["stock_symbol"])
        sell_shares = db.execute("SELECT SUM(shares) FROM purchase WHERE (users_id = ?) AND (action = ?) AND (stock_symbol = ?)",
                                 session["user_id"], "sell", stock["stock_symbol"])

        # if share has no buy or has no sell make it = 0
        if sell_shares[0]["SUM(shares)"] == None:
            sell_shares[0]["SUM(shares)"] = 0
        if buy_shares[0]["SUM(shares)"] == None:
            buy_shares[0]["SUM(shares)"] = 0

        # find total share of stock
        total_shares = buy_shares[0]["SUM(shares)"] - sell_shares[0]["SUM(shares)"]

        # add share to stock's dict
        stock["share"] = total_shares

        # add current share price and total share price to stock's dict
        test = lookup(stock["stock_symbol"])
        stock["current_price"] = test["price"]
        stock["total_price"] = round(test["price"] * total_shares, 2)
        # print(stock)
        # without round : {'stock_symbol': 'NFLX', 'stock_name': 'Netflix Inc.', 'SUM(shares)': 6, 'current_price': 176.56, 'total_price': 1059.3600000000001}
        # with round : {'stock_symbol': 'NFLX', 'stock_name': 'Netflix Inc.', 'SUM(shares)': 6, 'current_price': 176.56, 'total_price': 1059.36}

    # remove any stock if it has 0 shares
    stocks = [stock for stock in stocks if not (stock["share"] == 0)]

    # get user's cash
    user_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

    # find the total cash that the user has
    stocks_total = 0
    for stock in stocks:
        stocks_total = stocks_total + stock["total_price"]

    # passing the stocks and user cash and total user cash to be displayed
    return render_template("index.html", stocks=stocks, user_cash=user_cash[0]["cash"], grand_total=stocks_total + user_cash[0]["cash"])


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "GET":
        return render_template("buy.html")
    else:
        # get the input of the user
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # date and time
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # get user's cash
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        # username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])#[0]["id"])

        # use lookup to get the stock that the user typed it's symbol
        stock = lookup(symbol)

        # check if the symbol is valid
        if not stock:
            return apology("must enter symbol")
        # check if the number is fraction or less than 0
        if not shares.isdigit():
            return apology("invalid shares")
        if int(shares) < 0:
            return apology("invalid shares")

        # check if the user cash is larger than the stock(s) price
        if user_cash[0]["cash"] >= (stock["price"] * int(shares)):
            # insert the new stock in data base action 'buy'
            db.execute("INSERT INTO purchase (stock_name, stock_symbol, stock_price, shares, users_id, time, action) VALUES(?, ?, ?, ?, ?, ?, ?)",
                       stock["name"], stock["symbol"], stock["price"], int(shares), session["user_id"], time, "buy")
            # update user cash
            new_cash = user_cash[0]["cash"] - (stock["price"] * int(shares))
            db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, session["user_id"])
        else:
            return apology("can't afford")

    return redirect("/")


@app.route("/history")
@login_required
def history():
    history_logs = db.execute("SELECT stock_symbol, stock_price, shares, time, action FROM purchase")
    # print(history_logs)
    # [{'stock_symbol': 'NFLX', 'stock_price': 176.56, 'shares': 2, 'time': '2022-07-14 10:58:12', 'action': 'buy'}]
    return render_template("history.html", logs=history_logs)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    # when accessing the page via GET, render the quote page to enter symbol
    if request.method == "GET":
        return render_template("quote.html")
    else:  # accessing via POST

        # getting what symbol did the user input
        symbol = request.form.get("symbol")

        # using the lookup func. to lookup the name, price and symbol and putting them in a dict
        result = lookup(symbol)

        # user typed a symbol that does not exist
        if not result:
            return apology("invalid symbol")
        # passing the name, price and symbol to quoted.html to show them
        else:
            return render_template("quoted.html", name=result["name"], price=usd(result["price"]), symbol=result["symbol"])


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

        # PERSONAL TOUCH: Require users’ passwords to have some number of letters, numbers, and/or symbols.
        # Minimum eight characters, at least one letter, one number and one special character:
        regex = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"
        result = re.match(regex, password)
        if not result:
            return apology("password must be 8 characters and have a letters, a number and a special character")

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


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    stocks = db.execute(
        "SELECT stock_symbol, stock_name FROM purchase WHERE users_id = ? GROUP BY stock_symbol", session["user_id"])
    # print(stocks)
    #[{'stock_symbol': 'G', 'stock_name': 'Genpact Ltd'}, {'stock_symbol': 'NFLX', 'stock_name': 'Netflix Inc.'}]

    # select the total number of shares of each stock
    for stock in stocks:
        buy_shares = db.execute("SELECT SUM(shares) FROM purchase WHERE (users_id = ?) AND (action = ?) AND (stock_symbol = ?)",
                                session["user_id"], "buy", stock["stock_symbol"])
        sell_shares = db.execute("SELECT SUM(shares) FROM purchase WHERE (users_id = ?) AND (action = ?) AND (stock_symbol = ?)",
                                 session["user_id"], "sell", stock["stock_symbol"])

        if sell_shares[0]["SUM(shares)"] == None:
            sell_shares[0]["SUM(shares)"] = 0
        if buy_shares[0]["SUM(shares)"] == None:
            buy_shares[0]["SUM(shares)"] = 0

        total_shares = buy_shares[0]["SUM(shares)"] - sell_shares[0]["SUM(shares)"]

        # add share in stocks list of dicts
        stock["share"] = total_shares

     # remove any stock if it has 0 shares
    stocks = [stock for stock in stocks if not (stock["share"] == 0)]

    exist_symbols = [sub['stock_symbol'] for sub in stocks]
    # print(exist_symbols)
    #['G', 'NFLX']

    if request.method == "GET":
        return render_template("sell.html", symbols=exist_symbols)
    else:
        # get time, symbol, shares, user cash and stock
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        user_cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        stock = lookup(symbol)

        # select the total number of shares of current stock
        buy_shares = db.execute(
            "SELECT SUM(shares) FROM purchase WHERE (users_id = ?) AND (action = ?) AND (stock_symbol = ?)", session["user_id"], "buy", symbol)
        sell_shares = db.execute(
            "SELECT SUM(shares) FROM purchase WHERE (users_id = ?) AND (action = ?) AND (stock_symbol = ?)", session["user_id"], "sell", symbol)

        if sell_shares[0]["SUM(shares)"] == None:
            sell_shares[0]["SUM(shares)"] = 0
        if buy_shares[0]["SUM(shares)"] == None:
            buy_shares[0]["SUM(shares)"] = 0

        total_shares = buy_shares[0]["SUM(shares)"] - sell_shares[0]["SUM(shares)"]

        # check errors
        if (not symbol) or (symbol not in exist_symbols):
            return apology("missing symbol")
        if int(shares) > total_shares:
            return apology("too many shares")

        # insert the new stock in data base action 'sell'
        db.execute("INSERT INTO purchase (stock_name, stock_symbol, stock_price, shares, users_id, time, action) VALUES(?, ?, ?, ?, ?, ?, ?)",
                   stock["name"], stock["symbol"], stock["price"], int(shares), session["user_id"], time, "sell")

        # update user cash
        new_cash = user_cash[0]["cash"] + (stock["price"] * int(shares))
        db.execute("UPDATE users SET cash = ? WHERE id = ?", new_cash, session["user_id"])

    return redirect("/")
