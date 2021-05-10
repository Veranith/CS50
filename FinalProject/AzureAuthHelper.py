import os
import msal
from flask import render_template, request, session, url_for

# https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-v2-python-webapp

# Validate needed Evironment varabiles are present. 
if not os.getenv("clientId"):
    raise ValueError("Need to define clientId environment variable")
if not os.getenv("clientSecret"):
    raise ValueError("Need to define clientSecret environment variable")
if not os.getenv("tenantId"):
    raise ValueError("Need to define tenantId environment variable")


SESSION_TYPE = "filesystem"
CLIENT_ID = os.getenv("clientId")
CLIENT_SECRET = os.getenv("clientSecret")
if not CLIENT_SECRET:
    raise ValueError("Need to define clientSecret environment variable")
AUTHORITY = "https://login.microsoftonline.com/" + os.getenv("tenantId")
REDIRECT_PATH = "/getAToken"
ENDPOINT = 'https://graph.microsoft.com/v1.0/users'
SCOPE = ["User.ReadBasic.All"]
SESSION_TYPE = "filesystem"  # Specifies the token cache should be stored in server-side session


def azureLoginHelper():
    """Log user in"""

    # Forget any user_id
    session.clear()

    session["flow"] = _build_auth_code_flow(scopes=SCOPE)
    return render_template("login.html", auth_url=session["flow"]["auth_uri"], version=msal.__version__)


def azureAuthorized():
    try:
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_auth_code_flow(
            session.get("flow", {}), request.args)
        if "error" in result:
            return render_template("error.html", result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    except ValueError:  # Usually caused by CSRF
        pass  # Simply ignore them
    return


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        CLIENT_ID, authority=authority or AUTHORITY,
        client_credential=CLIENT_SECRET, token_cache=cache)


def _build_auth_code_flow(authority=None, scopes=None):
    return _build_msal_app(authority=authority).initiate_auth_code_flow(
        scopes or [],
        redirect_uri=url_for("authorized", _external=True))

