from cs50 import get_string

def wordcount(str):
    counter = 0
    for i in range (len(str)):
        c = str[i];
        if c==' ':
            counter += 1;
    counter = counter + 1
    return counter

def charactercount(str):
    counter = 0
    for i in range (len(str)):
        c = str[i];
        if (c.isalpha()):
            counter +=1
    return counter

def sentencecount(str):
    counter = 0
    for i in range (len(str)):
        c = str[i]
        if c=='.' or c=='!' or c=='?':
            counter += 1
    return counter

def main():
    st = get_string("Text: ")
    numberwords = wordcount(st)
    numberletters= charactercount(st)
    numbersentences = sentencecount(st)
    L = numberletters / numberwords * 100.0
    S = numbersentences / numberwords * 100.0
    index = 0.0588 * L - 0.296 * S - 15.8
    if index > 16:
        print("Grade 16+");
    elif index < 1:
        print("Before Grade 1")
    else:
        print(f"Grade {round(index)}")

main()

