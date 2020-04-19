from flask import Flask, redirect, render_template, request
app = Flask(__name__)
todos = []


@app.route("/")
def tasks():
    return render_template("tasks.html", todos = todos)
@app.route("/add", methods = ["GET", "POST"])
def add():
    if request.method == "GET":
        return render_template("add.html")
    else:
        task = request.form.get("task")
        todos.append(task)

        return redirect("/")