#include<stdio.h> 
#include<cs50.h>
#include<string.h>
#include <ctype.h> 
int wordcount(string s); //initializing function to count words
int charactercount(string s); //initializing function to count characters
int sentencecount(string s); //initializing function to count sentences



int main(void) //main functon
{
  string st = get_string("Text: ");
  int numberwords = wordcount(st); //calling function
  int numberletters= charactercount(st); //calling function
  int numbersentences = sentencecount(st); //calling function
  float L = (float)numberletters / numberwords * 100.0; 
  float S = (float)numbersentences / numberwords * 100.0;
  float index = 0.0588 * L - 0.296 * S - 15.8; //calculating as instructed
  if(index>16) //conditional statement if grade is over 16
    {
        printf("Grade 16+\n");
    } 
    else if(index<1) //conditional statement if grade is less than 1
    {
        printf("Before Grade 1\n");
    }
    else
    {
        printf("Grade %.0f\n", index);
    }
}
    
int wordcount(string s) //function to count words
{
    int counter = 0; //counter integer
    for(int i = 0, n = strlen(s); i<n; i++)
    {
    char c = s[i];
    if (c==' ')
    {
            counter++;
        }
    }
    counter = counter +1;
    return counter;
}
    
int charactercount(string s) //function to count characters

    int counter = 0; //counter integer
    for(int i = 0, n = strlen(s); i<n; i++)
    {
        char c = s[i];
        if (isalpha(c))
        {
            counter++;
        }
    }
    return counter;


    
int sentencecount(string s) //function to count sentences
{
    int counter = 0; //counter integer
    for(int i = 0, n = strlen(s); i<n; i++)
    {
        char c = s[i];
        if ((c=='.')||(c=='!')||(c=='?'))
        {
            counter++;
        }
    }
    return counter;
}
