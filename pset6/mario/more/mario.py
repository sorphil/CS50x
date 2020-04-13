from cs50 import get_int
height = get_int("Height: \n")
while height <= 0:
    height = get_int("Height: \n")
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
    print("  ", end = "")
    j = 0
    while j <= i:
        print("#", end = "")
        j += 1
    print()
    i += 1