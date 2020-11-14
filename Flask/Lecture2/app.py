from cs50 import SQL
from flask import Flask, redirect, request, render_template

app = Flask(__name__)

db = SQL("sqlite:///lecture.db")

@app.route("/")
def index():
