#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <string.h>
#include<stdlib.h>


int main(int argc, string argv[])
{

    if (argc == 2) //counts number of arguments in command line
    {
        int k = atoi(argv[1]); //converts the string in argv[1] to integer
        bool valid = true; //boolean flag to check if key is valid
        int length = strlen(argv[1]); //stores length of key
        for (int i = 0; i < length; i++) //loop to check it's validity (ie if its a number or not)
        {
           char c = argv[1][i];
            if (isdigit(c) == false)
            {
                valid = false;
                i = length; //to break the loop
            }
        }
        if (valid==true) //if key is valid (ie contains only numbers)
        {    printf("Success\n");
             printf("%d\n", k);
             char alpha[] = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'};
             char Alpha[26];
             for(int i = 0; i<26; i++)
             {
               Alpha[i]= toupper(alpha[i]);
             }
            
            string s = get_string("plaintext: ");
            int n = strlen(s);

            printf("ciphertext: ");
               for (int i = 0; i<n; i++)
            {
            char c = s[i]; //checking each character
            
            if (isupper(c)) //if between' A' and 'Z'
            {
                int ch = (int) c; //converting into integer
                ch = ch-65;
                ch = (ch + k)%26;
                printf("%c", Alpha[ch]); //taking character from the uppercase alphabet array (ie equivalent as per key)
            }
            else if(islower(c)) // if between 'a' and 'z'
            {
               int ch = (int) c;
               ch = ch-97;
               ch = (ch + k) %26;
               printf("%c", alpha[ch]); //taking character from the uppercase alphabet array (ie equivalent as per key)
            }
            else if((islower(c)!=true)&&(isupper(c)!=true))
            {
                 printf("%c", c); //if its not a letter (ie a punction mark, space, etc.), it is unchanged 
            }
            
        } 
        printf("\n");
        }
        else if(valid == false) //if the key is not valid
        {
            printf("Usage: ./caesar key\n");
            return 1;
            
        }
        
    }
    else if (argc != 2) //if more than one argument is entered
    {
        printf("Usage: ./caesar key\n");
        printf("1");
        return 1;
    }

}