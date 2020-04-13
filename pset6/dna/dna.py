import sys
import os
import csv

def count(string, string1): #To count consecutive AGATC substrings
    length = len(string1)
    count = 0
    index = string.find(string1)
    if index == -1:
        return 0
    elif index > -1:
        count = 1
    maximum = 0 #max number of occurences
    while index < len(string):
        while string[index+length:index+(length*2)]==string1:
            index = index + length
            count += 1
        if string[index+length:index+(length*2)]!=string1:
            index += 1
            temp = count
            count = 0
        if maximum<temp:
            maximum = temp
            temp = 0
    return maximum

if len(sys.argv)!=3:
    print("python dna.py data.csv sequence.txt")
    exit()
if os.path.isfile(sys.argv[2]) and os.path.isfile(sys.argv[1]):
    with open(sys.argv[1], 'r') as file: #opening the database file for reading
        reader = csv.DictReader(file) #using Dict reader to store csv into dict
        database = []
        for row in reader:
            database.append(row)



    with open(sys.argv[2], 'r') as file1: #opening the sequence file for reading
        if sys.argv[1] == 'databases/large.csv':
            string = file1.read()
            AGATC = count(string, 'AGATC')
            TTTTTTCT = count(string, 'TTTTTTCT')
            AATG = count(string, 'AATG')
            TCTAG = count(string, 'TCTAG')
            GATA = count(string, 'GATA')
            TATC = count(string, 'TATC')
            GAAA = count(string, 'GAAA')
            TCTG = count(string, 'TCTG')
            for row in database:
                a = int(row["AGATC"])
                b = int(row["TTTTTTCT"])
                c = int(row["AATG"])
                d = int(row["TCTAG"])
                e = int(row["GATA"])
                f = int(row["TATC"])
                g = int(row["GAAA"])
                h = int(row["TCTG"])
                if AGATC == a and TTTTTTCT == b and AATG == c and TCTAG == d and GATA == e and TATC == f and GAAA == g and TCTG == h:
                    print(row["name"])
                    exit()
            print("No match")



        elif sys.argv[1] == 'databases/small.csv':
            string = file1.read()
            AGATC = count(string, 'AGATC')
            AATG = count(string, 'AATG')
            TATC = count(string, 'TATC')
            for row in database:
                j = int(row["AGATC"])
                k = int(row["AATG"])
                l = int(row["TATC"])
                if AGATC == j and AATG == k and TATC == l:
                    print(row["name"])
                    exit()
            print("No match")