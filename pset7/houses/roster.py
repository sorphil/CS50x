# TODO
import sys
import os
import csv
from cs50 import SQL
if len(sys.argv)!=2:
    print("python import.py 'house name' ")
    exit()
if sys.argv[1] == "Gryffindor" or sys.argv[1] == "Ravenclaw" or sys.argv[1] == "Hufflepuff" or sys.argv[1] == "Slytherin":
    db = SQL("sqlite:///students.db")
    house = sys.argv[1]
    students = db.execute("SELECT * FROM students WHERE house = (?) ORDER BY last", house)
    for row in students:
        if row["middle"] == "None":
            
            print(row["first"] + " " + row["last"] + " born in " + str(row["birth"]))
        else:
             print(row["first"] + " " + row["middle"] + " " + row["last"] + " born in " + str(row["birth"]))
   
    