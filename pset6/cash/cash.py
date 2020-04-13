from cs50 import get_float

fl = get_float("Change owed: ")
while fl <= 0:
    number = float(input("Change owed: "))
result = (fl * 100)




c = 0
while result >= 25:
    c += 1
    result -= 25
while result >= 10:
    c += 1
    result -= 10
while result >= 5:
    c += 1
    result -= 5
while result >= 1:
    c += 1
    result -= 1
print(c)