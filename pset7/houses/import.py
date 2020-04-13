# TODO
import sys
import os
import csv
from cs50 import SQL
            

if len(sys.argv)!=2:
    print("python import.py file.csv")
    exit()
if os.path.isfile(sys.argv[1]):
    db = SQL("sqlite:///students.db")
    with open(sys.argv[1], 'r') as file: #opening the database file for reading
        reader = csv.DictReader(file) #using Dict reader to store csv into dict
        database = []
        for row in reader:
            row["name"] = row["name"].split()
            length = len(row["name"])
            if length == 2:
                db.execute("INSERT INTO students (first, middle, last, house, birth) VALUES (?, ?, ?, ?, ?)", row["name"][0], "None", row["name"][1], row["house"], row["birth"] )
            elif length == 3:
                db.execute("INSERT INTO students (first, middle, last, house, birth) VALUES (?, ?, ?, ?, ?)", row["name"][0], row["name"][1], row["name"][2], row["house"], row["birth"] )