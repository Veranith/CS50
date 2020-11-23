import os
from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd    # type: ignore

# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = '4E3D0C88F9B04938DC89C27C0B4271E53'

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    cash = db.execute("SELECT cash FROM users WHERE id = :id;", id=session["user_id"])[0]['cash']

    stocks = db.execute("SELECT symbol, sum(qty) AS shares FROM transactions "
                        "WHERE user_id = :user_id GROUP BY symbol ORDER BY symbol;", 
                        user_id=session["user_id"])
    
    total = cash
    
    for stock in stocks:
        stock.update(lookup(stock['symbol']))
        total += (stock['price'] * stock['shares'])
        #stock.update()
        
    return render_template("index.html", stocks=stocks, cash=usd(cash), total=usd(total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide a symbol", 403)

        # Verify shares is an int >= 1
        shares = request.form.get("shares", type=int)
        if not (isinstance(shares, int) and shares >= 1):
            return apology("must provide a valid quantity of shares to buy", 403)
        
        quote = lookup(request.form.get("symbol"))
        if quote is None:
            return apology("Symbol doesn't exist", 403)
        
        cash = float(db.execute("SELECT * FROM users WHERE id = :id;", 
                                id=session["user_id"])[0]['cash'])
        
        # Check to make sure there is available cash for transaction
        if shares * quote["price"] > cash:
            return apology("You don't have enough cash to make this purchase", 403)
        
        # Add transaction
        db.execute("INSERT INTO transactions (user_id, symbol, qty, price, date)"
                   "VALUES(:user_id, :symbol, :qty, :price, :date);",
                   user_id=session['user_id'],
                   symbol=symbol.upper(),
                   qty=shares,
                   price=quote["price"],
                   date=datetime.now()
                   )

        # subract purchase from cash in DB
        db.execute("UPDATE users SET cash=:cash WHERE id = :id;",
                   cash=round(cash - (shares * quote["price"]), 2),
                   id=session["user_id"])
        
        flash("Successfully purchased.", "success")
        return redirect(url_for("index"))

    else:
        symbol = request.args.get('symbol')
        return render_template("buy.html", symbol=symbol)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    purchases = db.execute("SELECT * FROM transactions "
                "WHERE user_id = :user_id ORDER BY date DESC;", 
                user_id=session["user_id"])
    
    return render_template("history.html", purchases=purchases)


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
        rows = db.execute("SELECT * FROM users WHERE username = :username;",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        
        # Redirect user to home page and display successful login message
        flash('Successfully logged in!', 'success')
        return redirect(url_for('index'))

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
    """Get stock quote."""

    if request.method == "POST":
        if not request.form.get("symbol"):
            return apology("must provide a symbol", 403)
        
        quote = lookup(request.form.get("symbol"))
        
        if quote is None:
            return apology("Symbol doesn't exist", 403)

        return render_template("quoted.html", quote=quote)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif not (request.form.get("password") == request.form.get("confirmation")):
            return apology("passwords do not match", 403)

        # Ensure username is not already taken
        elif len(db.execute("SELECT * FROM users WHERE username = :username;",
                            username=request.form.get("username"))) > 0:
            return apology("username already taken", 403)
        
        db.execute("INSERT INTO users (username, hash) VALUES(:username,:hash);",
                   username=request.form.get("username"),
                   hash=generate_password_hash(request.form.get("password")))
        
        # not working, todo
        flash('Account successfully created!', 'success')

        # Redirect user to home page
        return redirect(url_for("login"))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":

        symbol = request.form.get("symbol")
        if not symbol:
            return apology("must provide a symbol", 403)

        # Verify shares is an int >= 1
        sellShares = request.form.get("shares", type=int)
        if not (isinstance(sellShares, int) and sellShares >= 1):
            return apology("must provide a valid quantity of shares to buy", 403)

        # Get and validate shares from DB
        rows = db.execute("SELECT sum(qty) AS shares FROM transactions "
                        "WHERE user_id = :user_id AND symbol = :symbol GROUP BY symbol;", 
                        user_id=session["user_id"],
                        symbol= symbol
                        )
        if len(rows) != 1:
            return apology("You don't own this stock.", 403)
        ownedShares = rows[0]['shares']

        # Check to make sure there is available shares for transaction
        if not (ownedShares >= sellShares and isinstance(sellShares, int)):
            return apology("You don't own this many shares.", 403)

        # get current quote for this symbol
        quote = lookup(request.form.get("symbol"))
        if quote is None:
            return apology("Symbol doesn't exist", 403)
        
        # Add transaction
        db.execute("INSERT INTO transactions (user_id, symbol, qty, price, date)"
                   "VALUES(:user_id, :symbol, :qty, :price, :date);",
                   user_id=session['user_id'],
                   symbol=symbol.upper(),
                   qty=(sellShares * -1),
                   price=quote["price"],
                   date=datetime.now()
                   )

        # add purchase to cash in DB
        cash = db.execute("SELECT cash FROM users WHERE id = :id;", id=session["user_id"])[0]['cash']
        db.execute("UPDATE users SET cash=:cash WHERE id = :id;",
                   cash=round(cash + (sellShares * quote["price"]), 2),
                   id=session["user_id"])
        
        flash("Successfully sold shares.", "success")
        return redirect(url_for("index"))

    else:
        symbol = request.args.get('symbol')
        return render_template("sell.html", symbol=symbol)

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == '__main__':
    app.run(debug=True) 