from flask import Flask, render_template, request, redirect
import random

app = Flask(__name__)

tasklist = ["test", "test2"]

@app.route("/")
def tasks():
    return render_template('tasks.html', tasklist=tasklist)

@app.route("/add", methods=['POST','GET'])
def add():
    if request.method == 'GET':
        return render_template("add.html")
    else:
        item = request.form.get("newitem")
        tasklist.append(item)
        return redirect("/")