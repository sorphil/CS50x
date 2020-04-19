from flask import Flask, redirect, render_template, request, session
from flask_session import Session

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False #meaning the session is not permanent
app.config["SESSION_TYPE"] = "filesystem" #the location of the data pertaining to sessions is stored in a filesystem
Session(app) #enable session for this web application

@app.route("/")
def tasks():
    if "todos" not in session: #if the user has a keyword "todos" in his current session
        session["todos"] = [] #initialize it as empty
    return render_template("tasks.html", todos = session["todos"])

@app.route("/add", methods = ["GET", "POST"])  #means can use both get and post functions
def add():
    if request.method == "GET":
        return render_template("add.html")
    else:
        task = request.form.get("task")
        session["todos"].append(task)

        return redirect("/")