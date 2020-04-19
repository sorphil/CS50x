from flask import Flask, render_template, request
app = Flask(__name__)
@app.route("/") #/ is the default route
def index():
    return render_template("index.html")

@app.route("/hello")#if you type /hello at the end of the url, it will do this function
def hello():
    name = request.args.get("name") #Obtains the form parameters of the name "name"
    if name == '':
        return render_template("error.html")
    return render_template("hello.html", name = name)