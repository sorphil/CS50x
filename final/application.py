import os

from cs50 import SQL #to enable db.execute
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd



# Configure application
app = Flask(__name__)


# Custom filter
app.jinja_env.filters["usd"] = usd


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db") # To access finance.db




@app.route("/")
@login_required
def index():
    """Show courses and grades """

    #Obtain type of user
    usertype = db.execute("SELECT type from 'users' WHERE id = :user_id",
                                user_id = session["user_id"])[0]["type"]


    #Check the type of user logged in
    if usertype == "a student":


        #Check the students year or grade level
        level = db.execute("SELECT level FROM users WHERE id = :user_id",
                            user_id = session["user_id"])


        #If he/she is a new user, they must specify their grade
        if level[0]["level"] ==None:
            flash("You haven't specified what year you are in")
            return redirect("/level")


        #Obtain all the courses they applied to
        courses = db.execute("SELECT course_id FROM students WHERE user_id = :user_id",
                                user_id = session["user_id"])


        #If they applied to any yet
        if len(courses) == 0:
            return apology("seems like you haven't applied to any courses, click the link in the navigation bar at the top to get started", 404)


        #Obtain balance and courses and display it on page
        else:
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]
            courses = db.execute("SELECT * FROM courses JOIN students ON courses.id = students.course_id WHERE students.user_id = :user_id ORDER BY 'subject', 'id'",
                                        user_id = session["user_id"])
            return render_template("studentpage.html", courses = courses, balance = balance)




    #If the user is an instructor
    elif usertype == "an instructor":


        #Obtain the courses under the instructor
        courses = db.execute("SELECT * FROM courses JOIN instructors ON courses.id = instructors.course_id WHERE instructors.user_id = :user_id ORDER BY courses.level, courses.subject, courses.id",
                                        user_id = session["user_id"])
        print(courses)

        #If they have not created any courses yet
        if len(courses) == 0:
            return apology("seems like you haven't created any courses, click the link in the navigation bar at the top to get started", 404)


        #Display the page containing all their courses
        else:
            return render_template("instructorpage.html", courses = courses)





@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 404)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"] # index is 0 as there is only one row where the username/password exists

        flash("Welcome back!")
        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect) GET is a request for a page whereas POST submits something
    else:
        return render_template("login.html")




@app.route("/createcourse", methods=["GET", "POST"])
@login_required
def createcourse():

    #Display the HTML fike
    if request.method =="GET":

        #Obtain the user type to prevent a student from to accessing this page
        usertype = db.execute("SELECT type FROM users WHERE id = :user_id",
                    user_id = session["user_id"])[0]["type"]

        if usertype == "a student":
            return apology("This page is for instructors only", 401)


        else:
            #Displays the list as a dropdown box for the instructor to select which subject their course is
            subjects = ["Mathematics", "Computer Science", "Chemistry", "Physics", "Biology", "Medicine", "Music", "Art", "Sociology", "Politics", "Religion"]
            return render_template("create.html", subjects=subjects)




    elif request.method =="POST":


        #Obtain values inputted by the user
        subject = request.form.get("subject")
        course = request.form.get("course")
        course_id = request.form.get("courseid")
        level = request.form.get("level")
        price = request.form.get("price")


        #If nothing is inputted in the text boxes
        if not course:
            return apology("Enter a course name", 403)
        if not course_id:
            return apology("Enter a course id", 403)


        #Obtain first and last name of instructor
        user_id = session["user_id"]
        fname = db.execute("SELECT first from users WHERE id = :user_id",
                            user_id = user_id)[0]["first"]
        lname = db.execute("SELECT last from users WHERE id = :user_id",
                            user_id = user_id)[0]["last"]


        #To check if a course name is taken or that it already exists
        rows = db.execute("SELECT * FROM 'courses' WHERE name = :course",
                          course=course)
        if len(rows) == 1:
            return apology("this course already exists", 403)


        #To check if a course id is taken or that it already exists
        cid = db.execute("SELECT * FROM 'courses' WHERE id = :cid",
                          cid=course_id)
        if len(cid) == 1:
            return apology("this course id already exists", 403)


        #Concatanating the strings and inserting it in the new course created by the instructor
        instructor = fname + " " + lname
        db.execute("INSERT into courses (id, instructor, name, total, subject, price, level) VALUES (:course_id, :instructor, :name, :total, :subject, :price, :level)",
                    course_id = course_id, instructor = instructor, name = course, total = 0, subject= subject, price = price, level = level);
        db.execute("INSERT into 'instructors' (user_id, course_id) VALUES (:user_id, :course_id)",
                    user_id = session["user_id"], course_id = course_id)
        flash("Course sucessfully created")
        return redirect("/")





@app.route("/applycourse", methods=["GET"])
@login_required
def applycourse():
        usertype = db.execute("SELECT type FROM users WHERE id = :user_id",
                    user_id = session["user_id"])[0]["type"]

        if usertype == "an instructor":
            return apology("This page is for students only", 401)

        return render_template("applycourse.html")









@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    """Change password"""
    if request.method == "GET":
        return render_template("change.html")
    elif request.method == "POST":
        password = request.form.get("password")

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 403)

         # Query database for username
        rows = db.execute("SELECT * FROM users WHERE id = :user_id",
                          user_id=session["user_id"])

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid password", 403)


        newpass = request.form.get("newpassword")
        confirm = request.form.get("newpasswordconf")

        #to ensure password is new
        if newpass == password:
            return apology("new password must be different", 403)

        # Ensure new password was submitted
        if not newpass:
            return apology("must provide new password", 403)

        # Ensure new password was submitted
        if not confirm:
            return apology("must provide confirmation password", 403)

        # If passwords do no match
        if newpass != confirm:
            return apology("must provide matching password", 403)

        hash = generate_password_hash(newpass)
        new_user_id = db.execute("UPDATE users SET hash = :hash WHERE id = :user_id",
                                  hash=hash, user_id=session["user_id"])
        flash("Password changed!")
        # Redirect user to home page
        return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    flash("Logged out!")

    # Redirect user to login form
    return redirect("/")




@app.route("/forgot", methods=["GET", "POST"])
def forgot():
    """Forgot password"""
    if request.method == "GET":
        return render_template("forgot.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 403)

         # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("invalid username and/or password", 403)


        newpass = request.form.get("newpassword")
        confirm = request.form.get("newpasswordconf")

        #to ensure password is new
        if newpass == password:
            return apology("new password must be different", 403)

        # Ensure new password was submitted
        if not newpass:
            return apology("must provide new password", 403)

        # Ensure new password was submitted
        if not confirm:
            return apology("must provide confirmation password", 403)

        # If passwords do no match
        if newpass != confirm:
            return apology("must provide matching password", 403)

        hash = generate_password_hash(newpass)
        new_user_id = db.execute("UPDATE users SET hash = :hash WHERE username = :username",
                                  hash=hash, username=username)
        flash("Password changed!")
        # Redirect user to home page
        return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    #Load up HTML file
    if request.method == "GET":
        return render_template("register.html")



    elif request.method == "POST":


        #Obtain all inputted values
        fname = request.form.get("fname")

        lname = request.form.get("lname")

        user=request.form.get("user")

        password = request.form.get("password")

        passwordconf = request.form.get("passwordconf")

        usertype = request.form.get("usertype")


        #If input fields are left empty
        if not fname:
            return apology("must provide first name", 403)

        if not lname:
            return apology("must provide last name", 403)

        if not user:
            return apology("must provide username", 403)

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 403)

        if not passwordconf:
            return apology("must provide confirmation password", 403)

        # If passwords do no match
        elif password != passwordconf:
            return apology("must provide matching password", 403)


        #To check if a username is taken
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("user"))
        if len(rows) == 1:
            return apology("a user has already taken that name", 403)



        else:

            #Generate a hash in place of the actual password for security
            hash = generate_password_hash(request.form.get("password"))
            new_user_id = db.execute("INSERT INTO users (first, last, username, hash, type) VALUES(:fname, :lname, :user, :hash, :usertype)",
                                 user=user, hash=hash, fname=fname, lname=lname, usertype=usertype)


            #if the user is a student as per their input, they are taken to a page to specify their grade
            if usertype =="a student":
                 return redirect("/")
            else:
                session["user_id"] = new_user_id
                flash("Registered!")
                # Redirect user to home page
                return redirect("/")



@app.route("/level", methods=["GET", "POST"])
@login_required
def level():

    #Load up HTML file
    if request.method =="GET":
        usertype = db.execute("SELECT type FROM users WHERE id = :user_id",
                                user_id = session["user_id"])[0]["type"]
        if usertype == "a student":
            level = db.execute("SELECT level FROM users WHERE id = :user_id",
            user_id = session["user_id"])
            if len(level) != 1:
                return apology("You have already specified your year", 400)
            return render_template("level.html")
        elif usertype =="an instructor":
            return apology("This page is only for students", 400)


    #Obtain year of the student from a dropdown list update their information in the database and initializing their balance as 20,000 by default
    elif request.method =="POST":
        level = request.form.get("level")
        db.execute("UPDATE users SET level = :level, balance = :balance WHERE id = :user_id",
                        user_id = session["user_id"], level = level, balance = 20000)

        return redirect("/")



@app.route("/grade", methods=["GET", "POST"])
@login_required
def grade():

    #Load up HTML file
    if request.method =="GET":
        usertype = db.execute("SELECT type FROM users WHERE id = :user_id",
                                user_id = session["user_id"])
        if usertype == "a student":
            return apology("This page is only for instructors", 400)
        else:
            cid = session["cid"]
            courses =   db.execute("SELECT * FROM courses JOIN grades ON courses.id = grades.course_id WHERE grades.instructor_id = :user_id AND courses.id = :cid AND grades.grade = 'Ungraded'ORDER BY subject, id",
                        user_id = session["user_id"], cid = cid)
            for row in courses:
                fname = db.execute("SELECT first FROM users WHERE id = :student_id",
                                    student_id = row["student_id"])
                lname = db.execute("SELECT last FROM users WHERE id = :student_id",
                                    student_id = row["student_id"])
                name = fname[0]["first"] + " " + lname[0]["last"]
                row["student_name"] = name
            return render_template("grade.html", courses = courses)
    if request.method =="POST":
        grade = request.form.get("grade")
        notes = request.form.get("notes")

        student_id = request.form.get("student")
        cid = session["cid"]
        db.execute("UPDATE grades SET notes = :notes, grade = :grade WHERE student_id = :student_id AND instructor_id = :user_id AND course_id = :cid;",
                    student_id = student_id, user_id = session["user_id"], grade = grade, notes = notes, cid = cid)
        flash("Successful")
        return redirect("/")




@app.route("/studentgrade")
@login_required
def studentgrade():
    if request.method =="GET":

        usertype = db.execute("SELECT type FROM users WHERE id = :user_id",
                            user_id = session["user_id"])[0]["type"]
        if usertype == "a student":
            courses =   db.execute("SELECT * FROM courses JOIN grades ON courses.id = grades.course_id WHERE grades.student_id = :user_id ORDER BY subject",
                        user_id = session["user_id"])
            return render_template("studentgrade.html", courses = courses)
        elif usertype == "an instructor":
            return apology("This page is for students only", 400)


@app.route("/instructorgrade", methods=["GET", "POST"])
@login_required
def instructorgrade():
    if request.method =="GET":

        usertype = db.execute("SELECT type FROM users WHERE id = :user_id",
                            user_id = session["user_id"])[0]["type"]
        if usertype == "a student":
            return apology("This page is for instructors only", 400)

        elif usertype == "an instructor":
            courses =   db.execute("SELECT * FROM courses JOIN grades ON courses.id = grades.course_id WHERE grades.instructor_id = :user_id ORDER BY subject;",
                        user_id = session["user_id"])
            for row in courses:
                fname = db.execute("SELECT first FROM users WHERE id = :student_id",
                                    student_id = row["student_id"])
                lname = db.execute("SELECT last FROM users WHERE id = :student_id",
                                    student_id = row["student_id"])
                name = fname[0]["first"] + " " + lname[0]["last"]
                row["student_name"] = name
            return render_template("instructorgrade.html", courses = courses)
    elif request.method == "POST":
        session['cid'] = request.form.get('cid')
        return redirect("/grade")




def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)































#Subjects


@app.route("/math", methods=["GET", "POST"])
@login_required
def math():

    #To load the HTML file
    if request.method =="GET":

        #Displaying all courses under a subject
        courses=db.execute("SELECT * FROM courses WHERE subject = 'Mathematics' ORDER BY courses.level, courses.id")
        return render_template("subjects/math.html", courses=courses)


    #To obtain input from the HTML file
    else:

        #Obtaining the id of the course applied to by the student
        cid = request.form.get("cid")


        #Obtaining total number of students
        total = db.execute("SELECT total FROM courses where id = :cid",
                            cid = cid)[0]["total"]


        #To check if user is appropriate class/level/year
        course_level = db.execute("SELECT level FROM courses WHERE id = :cid",
                        cid = cid)[0]["level"]
        user_level = db.execute("SELECT level FROM users WHERE id = :user_id",
                                user_id = session["user_id"])[0]["level"]
        if user_level != course_level:
            return apology("This course is not available for your class")


        #To check if user has already choses that class
        course_id= db.execute("SELECT id FROM courses JOIN students ON courses.id = students.course_id WHERE students.user_id = :user_id" ,
                            user_id = session["user_id"])
        flag = False
        for row in course_id:
            if int(row["id"])==int(cid):
                flag = True
                break
        if flag == True:
            return apology("You have already applied to this class", 400)


        #If the no one has applied to the course yet, initialized to 1
        if total == 0:
            total = 1
            db.execute("UPDATE courses SET total = :total  WHERE id = :cid",
                       cid = cid, total = total)
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)


            #Obtaining cost of the course from the database
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]

            #Obtaining the balance of the student account from the database
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]

            #Subtracting and updating the database of the user's new balance
            balance = balance - cost

            #To check if the user can afford the course
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied to course")
            return redirect("/")
        else:

            #Updating student database by adding the id if the course they applied to
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)

            #Incrementing total students and updating in the data base
            total = total + 1
            db.execute("UPDATE courses SET total = :total WHERE id = :cid",
                    cid = cid, total = total)

            #Again obtaining cost and balance to check if the user can afford it
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]
            balance = balance - cost
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)


            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied To Course")
            return redirect("/")

@app.route("/music", methods=["GET", "POST"])
@login_required
def music():
    #To load the HTML file
    if request.method =="GET":

        #Displaying all courses under a subject
        courses=db.execute("SELECT * FROM courses WHERE subject = 'Music' ORDER BY courses.level, courses.id")
        return render_template("subjects/music.html", courses=courses)


    #To obtain input from the HTML file
    else:

        #Obtaining the id of the course applied to by the student
        cid = request.form.get("cid")


        #Obtaining total number of students
        total = db.execute("SELECT total FROM courses where id = :cid",
                            cid = cid)[0]["total"]


        #To check if user is appropriate class/level/year
        course_level = db.execute("SELECT level FROM courses WHERE id = :cid",
                        cid = cid)[0]["level"]
        user_level = db.execute("SELECT level FROM users WHERE id = :user_id",
                                user_id = session["user_id"])[0]["level"]
        if user_level != course_level:
            return apology("This course is not available for your class")


        #To check if user has already choses that class
        course_id= db.execute("SELECT id FROM courses JOIN students ON courses.id = students.course_id WHERE students.user_id = :user_id" ,
                            user_id = session["user_id"])
        flag = False
        for row in course_id:
            if int(row["id"])==int(cid):
                flag = True
                break
        if flag == True:
            return apology("You have already applied to this class", 400)


        #If the no one has applied to the course yet, initialized to 1
        if total == 0:
            total = 1
            db.execute("UPDATE courses SET total = :total  WHERE id = :cid",
                       cid = cid, total = total)
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)


            #Obtaining cost of the course from the database
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]

            #Obtaining the balance of the student account from the database
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]

            #Subtracting and updating the database of the user's new balance
            balance = balance - cost

            #To check if the user can afford the course
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])

            flash("Applied to course")
            return redirect("/")
        else:

            #Updating student database by adding the id if the course they applied to
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)

            #Incrementing total students and updating in the data base
            total = total + 1
            db.execute("UPDATE courses SET total = :total WHERE id = :cid",
                    cid = cid, total = total)

            #Again obtaining cost and balance to check if the user can afford it
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]
            balance = balance - cost
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied To Course")
            return redirect("/")


@app.route("/csc", methods=["GET", "POST"])
@login_required
def csc():
    #To load the HTML file
    if request.method =="GET":

        #Displaying all courses under a subject
        courses=db.execute("SELECT * FROM courses WHERE subject = 'Computer Science' ORDER BY courses.level, courses.id")
        return render_template("subjects/csc.html", courses=courses)


    #To obtain input from the HTML file
    else:

        #Obtaining the id of the course applied to by the student
        cid = request.form.get("cid")


        #Obtaining total number of students
        total = db.execute("SELECT total FROM courses where id = :cid",
                            cid = cid)[0]["total"]


        #To check if user is appropriate class/level/year
        course_level = db.execute("SELECT level FROM courses WHERE id = :cid",
                        cid = cid)[0]["level"]
        user_level = db.execute("SELECT level FROM users WHERE id = :user_id",
                                user_id = session["user_id"])[0]["level"]
        if user_level != course_level:
            return apology("This course is not available for your class")


        #To check if user has already choses that class
        course_id= db.execute("SELECT id FROM courses JOIN students ON courses.id = students.course_id WHERE students.user_id = :user_id" ,
                            user_id = session["user_id"])
        flag = False
        for row in course_id:
            if int(row["id"])==int(cid):
                flag = True
                break
        if flag == True:
            return apology("You have already applied to this class", 400)


        #If the no one has applied to the course yet, initialized to 1
        if total == 0:
            total = 1
            db.execute("UPDATE courses SET total = :total  WHERE id = :cid",
                       cid = cid, total = total)
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)


            #Obtaining cost of the course from the database
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]

            #Obtaining the balance of the student account from the database
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]

            #Subtracting and updating the database of the user's new balance
            balance = balance - cost

            #To check if the user can afford the course
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied to course")
            return redirect("/")
        else:

            #Updating student database by adding the id if the course they applied to
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)

            #Incrementing total students and updating in the data base
            total = total + 1
            db.execute("UPDATE courses SET total = :total WHERE id = :cid",
                    cid = cid, total = total)

            #Again obtaining cost and balance to check if the user can afford it
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]
            balance = balance - cost
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied To Course")
            return redirect("/")


@app.route("/chem", methods=["GET", "POST"])
@login_required
def chem():
    #To load the HTML file
    if request.method =="GET":

        #Displaying all courses under a subject
        courses=db.execute("SELECT * FROM courses WHERE subject = 'Chemistry' ORDER BY courses.level, courses.id")
        return render_template("subjects/chem.html", courses=courses)


    #To obtain input from the HTML file
    else:

        #Obtaining the id of the course applied to by the student
        cid = request.form.get("cid")


        #Obtaining total number of students
        total = db.execute("SELECT total FROM courses where id = :cid",
                            cid = cid)[0]["total"]


        #To check if user is appropriate class/level/year
        course_level = db.execute("SELECT level FROM courses WHERE id = :cid",
                        cid = cid)[0]["level"]
        user_level = db.execute("SELECT level FROM users WHERE id = :user_id",
                                user_id = session["user_id"])[0]["level"]
        if user_level != course_level:
            return apology("This course is not available for your class", 400)


        #To check if user has already choses that class
        course_id= db.execute("SELECT id FROM courses JOIN students ON courses.id = students.course_id WHERE students.user_id = :user_id" ,
                            user_id = session["user_id"])
        flag = False
        for row in course_id:
            if int(row["id"])==int(cid):
                flag = True
                break
        if flag == True:
            return apology("You have already applied to this class", 400)


        #If the no one has applied to the course yet, initialized to 1
        if total == 0:
            total = 1
            db.execute("UPDATE courses SET total = :total  WHERE id = :cid",
                       cid = cid, total = total)
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)


            #Obtaining cost of the course from the database
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]

            #Obtaining the balance of the student account from the database
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]

            #Subtracting and updating the database of the user's new balance
            balance = balance - cost

            #To check if the user can afford the course
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied to course")
            return redirect("/")
        else:

            #Updating student database by adding the id if the course they applied to
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)

            #Incrementing total students and updating in the data base
            total = total + 1
            db.execute("UPDATE courses SET total = :total WHERE id = :cid",
                    cid = cid, total = total)

            #Again obtaining cost and balance to check if the user can afford it
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]
            balance = balance - cost
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied To Course")
            return redirect("/")


@app.route("/phys", methods=["GET", "POST"])
@login_required
def phys():
    #To load the HTML file
    if request.method =="GET":

        #Displaying all courses under a subject
        courses=db.execute("SELECT * FROM courses WHERE subject = 'Physics' ORDER BY courses.level, courses.id")
        return render_template("subjects/phys.html", courses=courses)


    #To obtain input from the HTML file
    else:

        #Obtaining the id of the course applied to by the student
        cid = request.form.get("cid")


        #Obtaining total number of students
        total = db.execute("SELECT total FROM courses where id = :cid",
                            cid = cid)[0]["total"]


        #To check if user is appropriate class/level/year
        course_level = db.execute("SELECT level FROM courses WHERE id = :cid",
                        cid = cid)[0]["level"]
        user_level = db.execute("SELECT level FROM users WHERE id = :user_id",
                                user_id = session["user_id"])[0]["level"]
        if user_level != course_level:
            return apology("This course is not available for your class")


        #To check if user has already choses that class
        course_id= db.execute("SELECT id FROM courses JOIN students ON courses.id = students.course_id WHERE students.user_id = :user_id" ,
                            user_id = session["user_id"])
        flag = False
        for row in course_id:
            if int(row["id"])==int(cid):
                flag = True
                break
        if flag == True:
            return apology("You have already applied to this class", 400)


        #If the no one has applied to the course yet, initialized to 1
        if total == 0:
            total = 1
            db.execute("UPDATE courses SET total = :total  WHERE id = :cid",
                       cid = cid, total = total)
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)


            #Obtaining cost of the course from the database
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]

            #Obtaining the balance of the student account from the database
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]

            #Subtracting and updating the database of the user's new balance
            balance = balance - cost

            #To check if the user can afford the course
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied to course")
            return redirect("/")
        else:

            #Updating student database by adding the id if the course they applied to
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)

            #Incrementing total students and updating in the data base
            total = total + 1
            db.execute("UPDATE courses SET total = :total WHERE id = :cid",
                    cid = cid, total = total)

            #Again obtaining cost and balance to check if the user can afford it
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]
            balance = balance - cost
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied To Course")
            return redirect("/")


@app.route("/art", methods=["GET", "POST"])
@login_required
def art():
    #To load the HTML file
    if request.method =="GET":

        #Displaying all courses under a subject
        courses=db.execute("SELECT * FROM courses WHERE subject = 'Art' ORDER BY courses.level, courses.id")
        return render_template("subjects/art.html", courses=courses)


    #To obtain input from the HTML file
    else:

        #Obtaining the id of the course applied to by the student
        cid = request.form.get("cid")


        #Obtaining total number of students
        total = db.execute("SELECT total FROM courses where id = :cid",
                            cid = cid)[0]["total"]


        #To check if user is appropriate class/level/year
        course_level = db.execute("SELECT level FROM courses WHERE id = :cid",
                        cid = cid)[0]["level"]
        user_level = db.execute("SELECT level FROM users WHERE id = :user_id",
                                user_id = session["user_id"])[0]["level"]
        if user_level != course_level:
            return apology("This course is not available for your class")


        #To check if user has already choses that class
        course_id= db.execute("SELECT id FROM courses JOIN students ON courses.id = students.course_id WHERE students.user_id = :user_id" ,
                            user_id = session["user_id"])
        flag = False
        for row in course_id:
            if int(row["id"])==int(cid):
                flag = True
                break
        if flag == True:
            return apology("You have already applied to this class", 400)


        #If the no one has applied to the course yet, initialized to 1
        if total == 0:
            total = 1
            db.execute("UPDATE courses SET total = :total  WHERE id = :cid",
                       cid = cid, total = total)
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)


            #Obtaining cost of the course from the database
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]

            #Obtaining the balance of the student account from the database
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]

            #Subtracting and updating the database of the user's new balance
            balance = balance - cost

            #To check if the user can afford the course
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied to course")
            return redirect("/")
        else:

            #Updating student database by adding the id if the course they applied to
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)

            #Incrementing total students and updating in the data base
            total = total + 1
            db.execute("UPDATE courses SET total = :total WHERE id = :cid",
                    cid = cid, total = total)

            #Again obtaining cost and balance to check if the user can afford it
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]
            balance = balance - cost
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied To Course")
            return redirect("/")


@app.route("/religion", methods=["GET", "POST"])
@login_required
def religion():
    #To load the HTML file
    if request.method =="GET":

        #Displaying all courses under a subject
        courses=db.execute("SELECT * FROM courses WHERE subject = 'Religion' ORDER BY courses.level, courses.id")
        return render_template("subjects/religion.html", courses=courses)


    #To obtain input from the HTML file
    else:

        #Obtaining the id of the course applied to by the student
        cid = request.form.get("cid")


        #Obtaining total number of students
        total = db.execute("SELECT total FROM courses where id = :cid",
                            cid = cid)[0]["total"]


        #To check if user is appropriate class/level/year
        course_level = db.execute("SELECT level FROM courses WHERE id = :cid",
                        cid = cid)[0]["level"]
        user_level = db.execute("SELECT level FROM users WHERE id = :user_id",
                                user_id = session["user_id"])[0]["level"]
        if user_level != course_level:
            return apology("This course is not available for your class")


        #To check if user has already choses that class
        course_id= db.execute("SELECT id FROM courses JOIN students ON courses.id = students.course_id WHERE students.user_id = :user_id" ,
                            user_id = session["user_id"])
        flag = False
        for row in course_id:
            if int(row["id"])==int(cid):
                flag = True
                break
        if flag == True:
            return apology("You have already applied to this class", 400)


        #If the no one has applied to the course yet, initialized to 1
        if total == 0:
            total = 1
            db.execute("UPDATE courses SET total = :total  WHERE id = :cid",
                       cid = cid, total = total)
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)


            #Obtaining cost of the course from the database
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]

            #Obtaining the balance of the student account from the database
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]

            #Subtracting and updating the database of the user's new balance
            balance = balance - cost

            #To check if the user can afford the course
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied to course")
            return redirect("/")
        else:

            #Updating student database by adding the id if the course they applied to
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)

            #Incrementing total students and updating in the data base
            total = total + 1
            db.execute("UPDATE courses SET total = :total WHERE id = :cid",
                    cid = cid, total = total)

            #Again obtaining cost and balance to check if the user can afford it
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]
            balance = balance - cost
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied To Course")
            return redirect("/")


@app.route("/bio", methods=["GET", "POST"])
@login_required
def bio():
    #To load the HTML file
    if request.method =="GET":

        #Displaying all courses under a subject
        courses=db.execute("SELECT * FROM courses WHERE subject = 'Biology' ORDER BY courses.level, courses.id")
        return render_template("subjects/bio.html", courses=courses)


    #To obtain input from the HTML file
    else:

        #Obtaining the id of the course applied to by the student
        cid = request.form.get("cid")


        #Obtaining total number of students
        total = db.execute("SELECT total FROM courses where id = :cid",
                            cid = cid)[0]["total"]


        #To check if user is appropriate class/level/year
        course_level = db.execute("SELECT level FROM courses WHERE id = :cid",
                        cid = cid)[0]["level"]
        user_level = db.execute("SELECT level FROM users WHERE id = :user_id",
                                user_id = session["user_id"])[0]["level"]
        if user_level != course_level:
            return apology("This course is not available for your class")


        #To check if user has already choses that class
        course_id= db.execute("SELECT id FROM courses JOIN students ON courses.id = students.course_id WHERE students.user_id = :user_id" ,
                            user_id = session["user_id"])
        flag = False
        for row in course_id:
            if int(row["id"])==int(cid):
                flag = True
                break
        if flag == True:
            return apology("You have already applied to this class", 400)


        #If the no one has applied to the course yet, initialized to 1
        if total == 0:
            total = 1
            db.execute("UPDATE courses SET total = :total  WHERE id = :cid",
                       cid = cid, total = total)
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)


            #Obtaining cost of the course from the database
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]

            #Obtaining the balance of the student account from the database
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]

            #Subtracting and updating the database of the user's new balance
            balance = balance - cost

            #To check if the user can afford the course
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied to course")
            return redirect("/")
        else:

            #Updating student database by adding the id if the course they applied to
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)

            #Incrementing total students and updating in the data base
            total = total + 1
            db.execute("UPDATE courses SET total = :total WHERE id = :cid",
                    cid = cid, total = total)

            #Again obtaining cost and balance to check if the user can afford it
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]
            balance = balance - cost
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied To Course")
            return redirect("/")


@app.route("/med", methods=["GET", "POST"])
@login_required
def med():
    #To load the HTML file
    if request.method =="GET":

        #Displaying all courses under a subject
        courses=db.execute("SELECT * FROM courses WHERE subject = 'Medicine' ORDER BY courses.level, courses.id")
        return render_template("subjects/med.html", courses=courses)


    #To obtain input from the HTML file
    else:

        #Obtaining the id of the course applied to by the student
        cid = request.form.get("cid")


        #Obtaining total number of students
        total = db.execute("SELECT total FROM courses where id = :cid",
                            cid = cid)[0]["total"]


        #To check if user is appropriate class/level/year
        course_level = db.execute("SELECT level FROM courses WHERE id = :cid",
                        cid = cid)[0]["level"]
        user_level = db.execute("SELECT level FROM users WHERE id = :user_id",
                                user_id = session["user_id"])[0]["level"]
        if user_level != course_level:
            return apology("This course is not available for your class")


        #To check if user has already choses that class
        course_id= db.execute("SELECT id FROM courses JOIN students ON courses.id = students.course_id WHERE students.user_id = :user_id" ,
                            user_id = session["user_id"])
        flag = False
        for row in course_id:
            if int(row["id"])==int(cid):
                flag = True
                break
        if flag == True:
            return apology("You have already applied to this class", 400)


        #If the no one has applied to the course yet, initialized to 1
        if total == 0:
            total = 1
            db.execute("UPDATE courses SET total = :total  WHERE id = :cid",
                       cid = cid, total = total)
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)


            #Obtaining cost of the course from the database
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]

            #Obtaining the balance of the student account from the database
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]

            #Subtracting and updating the database of the user's new balance
            balance = balance - cost

            #To check if the user can afford the course
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied to course")
            return redirect("/")
        else:

            #Updating student database by adding the id if the course they applied to
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)

            #Incrementing total students and updating in the data base
            total = total + 1
            db.execute("UPDATE courses SET total = :total WHERE id = :cid",
                    cid = cid, total = total)

            #Again obtaining cost and balance to check if the user can afford it
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]
            balance = balance - cost
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied To Course")
            return redirect("/")



@app.route("/politics", methods=["GET", "POST"])
@login_required
def politics():
    #To load the HTML file
    if request.method =="GET":

        #Displaying all courses under a subject
        courses=db.execute("SELECT * FROM courses WHERE subject = 'Politics' ORDER BY courses.level, courses.id")
        return render_template("subjects/politics.html", courses=courses)


    #To obtain input from the HTML file
    else:

        #Obtaining the id of the course applied to by the student
        cid = request.form.get("cid")


        #Obtaining total number of students
        total = db.execute("SELECT total FROM courses where id = :cid",
                            cid = cid)[0]["total"]


        #To check if user is appropriate class/level/year
        course_level = db.execute("SELECT level FROM courses WHERE id = :cid",
                        cid = cid)[0]["level"]
        user_level = db.execute("SELECT level FROM users WHERE id = :user_id",
                                user_id = session["user_id"])[0]["level"]
        if user_level != course_level:
            return apology("This course is not available for your class")


        #To check if user has already choses that class
        course_id= db.execute("SELECT id FROM courses JOIN students ON courses.id = students.course_id WHERE students.user_id = :user_id" ,
                            user_id = session["user_id"])
        flag = False
        for row in course_id:
            if int(row["id"])==int(cid):
                flag = True
                break
        if flag == True:
            return apology("You have already applied to this class", 400)


        #If the no one has applied to the course yet, initialized to 1
        if total == 0:
            total = 1
            db.execute("UPDATE courses SET total = :total  WHERE id = :cid",
                       cid = cid, total = total)
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)


            #Obtaining cost of the course from the database
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]

            #Obtaining the balance of the student account from the database
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]

            #Subtracting and updating the database of the user's new balance
            balance = balance - cost

            #To check if the user can afford the course
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied to course")
            return redirect("/")
        else:

            #Updating student database by adding the id if the course they applied to
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)

            #Incrementing total students and updating in the data base
            total = total + 1
            db.execute("UPDATE courses SET total = :total WHERE id = :cid",
                    cid = cid, total = total)

            #Again obtaining cost and balance to check if the user can afford it
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]
            balance = balance - cost
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied To Course")
            return redirect("/")


@app.route("/socio", methods=["GET", "POST"])
@login_required
def socio():
    #To load the HTML file
    if request.method =="GET":

        #Displaying all courses under a subject
        courses=db.execute("SELECT * FROM courses WHERE subject = 'Sociology' ORDER BY courses.level, courses.id")
        return render_template("subjects/socio.html", courses=courses)


    #To obtain input from the HTML file
    else:

        #Obtaining the id of the course applied to by the student
        cid = request.form.get("cid")


        #Obtaining total number of students
        total = db.execute("SELECT total FROM courses where id = :cid",
                            cid = cid)[0]["total"]


        #To check if user is appropriate class/level/year
        course_level = db.execute("SELECT level FROM courses WHERE id = :cid",
                        cid = cid)[0]["level"]
        user_level = db.execute("SELECT level FROM users WHERE id = :user_id",
                                user_id = session["user_id"])[0]["level"]
        if user_level != course_level:
            return apology("This course is not available for your class")


        #To check if user has already choses that class
        course_id= db.execute("SELECT id FROM courses JOIN students ON courses.id = students.course_id WHERE students.user_id = :user_id" ,
                            user_id = session["user_id"])
        flag = False
        for row in course_id:
            if int(row["id"])==int(cid):
                flag = True
                break
        if flag == True:
            return apology("You have already applied to this class", 400)


        #If the no one has applied to the course yet, initialized to 1
        if total == 0:
            total = 1
            db.execute("UPDATE courses SET total = :total  WHERE id = :cid",
                       cid = cid, total = total)
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)


            #Obtaining cost of the course from the database
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]

            #Obtaining the balance of the student account from the database
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]

            #Subtracting and updating the database of the user's new balance
            balance = balance - cost

            #To check if the user can afford the course
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied to course")
            return redirect("/")
        else:

            #Updating student database by adding the id if the course they applied to
            db.execute("INSERT INTO students (course_id, user_id) VALUES(:cid, :user_id)",
                        user_id = session["user_id"], cid = cid)

            #Incrementing total students and updating in the data base
            total = total + 1
            db.execute("UPDATE courses SET total = :total WHERE id = :cid",
                    cid = cid, total = total)

            #Again obtaining cost and balance to check if the user can afford it
            cost = db.execute("SELECT price FROM courses WHERE id = :cid",
                                cid = cid)[0]["price"]
            balance = db.execute("SELECT balance FROM users WHERE id = :user_id",
                                    user_id = session["user_id"])[0]["balance"]
            balance = balance - cost
            if balance < 0:
                return apology("Sorry, you can't afford this course", 400)

            #Get the id of the instructor of the course
            instructor_id = db.execute("SELECT user_id FROM instructors WHERE course_id = :cid",
                            cid = cid)[0]["user_id"]

            #Add the course to the gradebook
            db.execute("INSERT INTO grades (student_id, course_id, instructor_id) VALUES (:user_id, :cid, :instructor_id)",
                        user_id = session["user_id"], cid = cid, instructor_id = instructor_id)

            db.execute("UPDATE users SET balance = :balance WHERE id = :user_id",
                        balance = balance, user_id = session["user_id"])
            flash("Applied To Course")
            return redirect("/")


