from typing import final
from flask import redirect, render_template, session
from functools import wraps
from AzureHelpers import open_azure_db, close_azure_db # type:ignore
import logging


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def getClientInfo(clientNumber):
    """Get client info from Azure Mysql DB"""
    sql = "SELECT * FROM appClientInfo WHERE clientNumber = %s LIMIT 1"
    values = (clientNumber,)
    return sqlQuery(sql, values)


def getKitchenMeal(mealDate):
    """Get client info from Azure Mysql DB"""

    sql = 'SELECT * FROM routesheetweek '\
          'WHERE MealDate = %s AND MealType = "Hot Meal" '\
          'ORDER BY RouteName ASC, RouteOrder'
    values = (mealDate,)    
    return sqlQuery(sql, values)


def getRouteNames():
    """Get list of routes"""

    sql = 'SELECT RouteName FROM routesheetweek '\
          'GROUP BY RouteName ORDER BY RouteName'
    return sqlQuery(sql)


def getRouteData(routeName, mealDate):
    """Get list of routes"""

    sql = 'SELECT DISTINCT LastName, FirstName, RouteName, RouteOrder, Address, Phone, '\
          'DietName, HighlightInstruction, Instruction, TotalHotMeal, TotalFrozenMeal '\
          'FROM routesheetweek WHERE RouteName = %s and MealDate = %s '\
          'ORDER BY RouteName, RouteOrder'
    values = (routeName, mealDate)
    return sqlQuery(sql, values)


def sqlQuery(SQL, values=None):
    """Run Queries on Azure Mysql DB"""
    
    db, cursor = open_azure_db()
    
    try:
        logging.info(f"Query: {SQL}")
        logging.info(f"Values: {values}")
        cursor.execute(SQL, values)
        dbResult = cursor.fetchall()
        logging.info(f"Fetched {len(dbResult)} rows.")
    finally:
        close_azure_db(db, cursor)
    
    if dbResult is None:
        return False
    return dbResult

