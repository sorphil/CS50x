from cs50 import SQL
from flask import Flask, session, render_template, request, redirect

app = Flask(__name__)
db = SQL("sqlite:///lecture.db")

@app.route("/")
def index():
    rows = db.execute("SELECT * FROM registrants") #saving or storing the result from this query into a variable
    return render_template("index.html", indexrows = rows)

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        name = request.form.get("name") #Getting input from the one with name "name" from form
        email = request.form.get("email") #Getting input from the one with name "email" from form
        if name == '' and email =='':
            msg = "Please provide a name and email address"
            return render_template("apology.html", message = msg)
        if name == '':
            msg = "Please provide a name"
            return render_template("apology.html", message = msg)
        if email =='':
            msg = "Please provide an email address"
            return render_template("apology.html", message = msg)

        db.execute("INSERT INTO registrants ('name', 'email') VALUES (?, ?)", name, email)
        # OR ("INSERT INTO registrants ('name', 'email') VALUES (:name1, :email1)", name1 = name, email1 = email)
        return redirect("/")