import os
import logging
import requests
from requests import status_codes
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.middleware.proxy_fix import ProxyFix
from helpers import apology, login_required, getClientInfo, getKitchenMeal, getRouteNames, getRouteData # type:ignore
from AzureAuthHelper import azureLoginHelper, azureAuthorized, REDIRECT_PATH # type:ignore


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# This section is needed for url_for("foo", _external=True)
# See also https://flask.palletsprojects.com/en/1.0.x/deploying/wsgi-standalone/#proxy-setups
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Set logging level
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))

# global variables
routeNames = None


# Begin Routes
@app.route("/")
@login_required
def index():
    """Main page"""
    return render_template("home.html", navOpen=True)


@app.route("/clients", methods=["GET", "POST"])
@login_required
def clients():
    """Show Client data"""

    if request.method == "POST":
        clientNumber = request.form.get("clientNumber")
        if not clientNumber:
            return apology("must provide a client number", 403)
        clientInfo = getClientInfo(clientNumber)
        if len(clientInfo) > 0 and clientInfo != False:
            return render_template("client.html", clientInfo=clientInfo[0])
        flash("Client not found.", "warning")
    return render_template("clientreq.html")


@app.route("/kitchen", methods=["GET", "POST"])
@login_required
def kitchen():
    """Show kitchen meal data"""
    if request.method == "POST":
        mealDate = request.form.get("mealDate")
        if not mealDate:
            return apology("must provide a meal date", 403)
        clientMeals = getKitchenMeal(mealDate)
        if len(clientMeals) > 0:
            return render_template("kitchen.html", clientMeals=clientMeals)
        flash("Meals not found for this date.", "warning")
    
    return render_template("kitchenreq.html")


@app.route("/routes", methods=["GET", "POST"])
@login_required
def routes():
    """Display Routes"""
    global routeNames
    if request.method == "POST":
        # Validate recieved args are present
        route = request.form.get("route")
        if not route:
            flash("Must select a route", "warning")
            return redirect(url_for("routes"))
        mealDate = request.form.get("mealDate")
        if not mealDate:
            flash("Must select a meal date.", "warning")
            return redirect(url_for("routes"))
        
        routeData = getRouteData(route, mealDate)
        if len(routeData) > 0:
            return render_template("route.html", routeNames=routeNames, routeData=routeData)
        flash("Meals not found for this route.", "warning")

    if routeNames is None:
        routeNames = getRouteNames()

    return render_template("routereq.html", routeNames=routeNames)


@app.route("/tools")
@login_required
def tools():
    """MoW Tools"""

    return render_template("tools.html")


@app.route("/addclientmeal", methods=["GET", "POST"])
# @login_required
def addClientMeal():
    """MoW Add Single Client Weekly Meals"""

    if request.method == "POST":
        # Validate required args are present

        startDate = request.form.get("startDate")
        if not startDate:
            flash("Must select a start date.", "warning")
            return redirect(url_for("addClientMeal"))

        # If clientId is present, then the information has been validated and we can call the API to generate the new meals
        clientId = request.form.get("clientId")
        if clientId:
            print("client id:", clientId)
            print("start:", startDate)

        # TODO process completed request

        clientNumber = request.form.get("clientNumber")
        if not clientNumber:
            flash("Must enter a client number", "warning")
            return redirect(url_for("addClientMeal"))

        # Get needed info for API from environment
        fKey =  os.environ.get("addClientMealsFKey")
        fAppURL = os.environ.get("addClientMealsURL")
    
        if (fKey is None) or (fAppURL is None):
            raise ValueError("Need to define addClientMealsFKey and addClientMealsURI environment variables")
        
        logging.info(f"Requesting client info for client number {clientNumber} from addClientMeal API.")
        result = requests.get(f"{fAppURL}api/AddClientMeal?code={fKey}&clientNumber={clientNumber}")
        logging.info(f"Request status code {result.status_code}.")

        if result.status_code == 204:
            flash("Client not found.", "warning")
            return redirect(url_for("addClientMeal"))

        if result.status_code == 200:
            clientInfo = result.json()
            print("Info:", clientInfo)
            return render_template("addclientmealverify.html", clientInfo=clientInfo, startDate=startDate)

        else:
            flash("addCLientMeal API call failed.", "warning")
        
        # if len(routeData) > 0:
        #     return render_template("route.html", routeNames=routeNames, routeData=routeData)
        # flash("Meals not found for this route.", "warning")

    return render_template("addclientmealreq.html")



@app.route("/login", methods=["GET"])
def login():
    """Log user in"""
    return azureLoginHelper()


@app.route(REDIRECT_PATH)
def authorized():
    """Is Authorized from Azure AD?"""
    
    azureAuthorized()

    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    """Log user out"""
    
    # Forget any user session
    session.clear()
    return redirect(url_for("index"))


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

