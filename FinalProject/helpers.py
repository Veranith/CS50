from flask import redirect, render_template, session
from functools import wraps
from AzureHelpers import open_azure_db, close_azure_db # type:ignore

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


def sqlQuery(SQL, values):
    """Run Queries on Azure Mysql DB"""
    db, cursor = open_azure_db()
    cursor.execute(SQL, values)
    dbResult = cursor.fetchall()
    close_azure_db(db, cursor)
    if dbResult is None:
        return False
    return dbResult

