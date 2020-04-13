#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <string.h>
#include<stdlib.h>

int main(int argc, string argv[])
{

    if (argc == 2) //counts number of arguments in command line
    {
        string key = argv[1];
        bool v = true; //boolean flag to check if  is valid
        bool v1 = true; //boolean flag to check if it contains 26 characters
        bool v2 = true; //boolean flag to check if it contains duplicates
        int length = strlen(argv[1]); //stores length of key
        for (int i = 0; i < length; i++) //loop to check if the characters are all letters
        {   
            char c = argv[1][i];
            if (isalpha(c))
            {
            }
            else
            {
                v = false;
                i = length; //to break the loop
            }
        }
        if(length==26) //if length is 26
        {
            for (int i = 0; i<length; i++) //two loops to check if there are any duplicates
        {
           for (int j = i+1; j<length -1; j++)
           {
               if(key[i]==key[j])
               {
                   v2 = false;
                   i = 26;
                   j = 26;
               }
           }
        }
        }
        
        
        if(length!=26)
        {
            v1= false;
        }
        if ((v==true)&&(v1==true)&&(v2==true))
        {
            char alpha[] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'}; //for comparison
            char Alpha[26];
             for(int i = 0; i<26; i++)
             {
               Alpha[i]= toupper(alpha[i]);
             }
             char k[26]; //to store key into a character array for comparison
             for (int i = 0; i< 26; i++)
             {
                 k[i] = key[i];
             }
             string s = get_string("plaintext: ");
             int n = strlen(s);
             printf("ciphertext: ");
              for(int i = 0; i<n; i++)
           {
            int flag = 0; //flag variable that results in 1 if the character's position from the string inputted is found in the alphabet array
            char ch = s[i];
            char r;
            if(isalpha(ch))
            {    for(int j = 0; j<26; j++)
                 {
                     if(ch==alpha[j]) 
                     {
                        flag = j; //this flag variable (ie position) stores the position which it then uses to obtain the corresponding character at "flag" position of the key
                      }
                     if(ch==Alpha[j])
                     {
                         flag = j;
                        }
                 }
                 if (islower(ch)) //if its lowercase, the key characters obtained are made lowercase as well
                 {
                     r = tolower(k[flag]);
                  }
                  else //if its uppercase, the key characters obtained are made uppercase as well
                  {
                    r= toupper(k[flag]);
                  }
                  printf("%c", r);
                }
            else //if the character is not a letter, it is printed normally
            {
                printf("%c", ch);
            }
        }
        printf("\n");
        }
        else if(v == false) //if the key is not valid
        {
            printf("Usage: ./substitution key\n");
             return 1;

        }
         else if(v2 == false) //if there are duplications
        {
            printf("Usage: ./substitution key\n");
             return 1;

        }

         else if((v==true)&&(v1==false)) //if the key contains only letters but does not have a length of 26
    {
        printf("Key must contain 26 characters.\n");
        return 1;
    }

    }
    else if (argc != 2) //if more than one argument is entered
    {
        printf("Usage: ./substitution key\n");
        return 1;
    }


}