import cs50
height =  cs50.get_int("Height: \n")
while height <= 0 or height > 8:
    height = cs50.get_int("Height: \n")

i = 0
while i < height:
    space = 0
    while space < height - i - 1:
        print(" ", end = "")
        space += 1
    j = 0
    while j <= i:
        print("#", end = "")
        j += 1
    print()
    i += 1