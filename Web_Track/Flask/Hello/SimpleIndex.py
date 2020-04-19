from flask import Flask, render_template
import random
app = Flask(__name__)
@app.route("/")
def index(): 
    number = random.randint(0,1)
    return render_template("index.html", value=number) #can take variables as well

@app.route("/goodbye")#if you type /goodbye at the end of the url, it will do this function
def bye():
    return "Goodbye, world!"