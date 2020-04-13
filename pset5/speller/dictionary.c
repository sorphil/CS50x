// Implements a dictionary's functionality

#include <stdbool.h>
#include <string.h>
#include <strings.h>
#include <ctype.h>
#include <stdio.h>
#include "dictionary.h"
#include <stdlib.h>

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;


// Number of buckets in hash table
const unsigned int N = 1000;
int Number_Of_Words = 0;

// Hash table
node *table[N];

// Returns true if word is in dictionary else false
bool check(const char *word)
{
    int len = strlen(word); //take length of string
    char copy[len+1]; //create another character array/string to convert to lowercase
    for(int i = 0; i < len+1; i++)
    {
        copy[i] = tolower(word[i]); //converting words into lowercase for them to have same hash value as the words in the dictionary
    }
    int h = hash(copy) % N;
    if(table[h] == NULL) //if that index of the array is empty
    {
        return false;
    }
    node *head = table[h]; //initializing the pointer to head of the index
    if(head!=NULL) //if the head is not NULL, or the index at the hashtable is not empty
    {
        node *cursor = head; //linking a cursor to the head
        while (cursor!=NULL)
        {
            if(strcasecmp (copy, cursor->word) == 0)
            {
                return true;
            }
            else
            {
                cursor = cursor->next;
            }
        }
    }
    return false;
}


// Hashes word to a number
unsigned long hash(const char *word) // By Dan Bernstein http://www.cse.yorku.ca/~oz/hash.html
{
    unsigned long hash = 5381;
    int c;

    while ((c = *word++))
    hash = ((hash << 5) + hash) + c; // hash * 33 + c
    return hash;
    
}


// Loads dictionary into memory, returning true if successful else false
bool load(const char *dictionary)
{
    // TODO
    
    FILE *file = fopen(dictionary, "r");
    if (file==NULL) //if file could not be opened
    {
        fclose(file);
        return false;
    }
    char word[LENGTH]; //initializing string
    
    for (int i = 0; i < 1000; i++) //initializing the hash table values as null
    {
        table[i] = NULL;
    }
    
    while (fscanf(file, "%s", word) != EOF)        //copying each word from the dictionary file to the word
    {

        node *n = malloc(sizeof(node)); //allocating memory for a new node
        if(n==NULL) //unable to allocate memory
        {
            unload();
            return false;
        }
        strcpy(n->word, word); //stores the string into the location given as the first argument
        unsigned long h = hash(word) % N;
        if(table[h] == NULL) //if nothing is linked to the array yet
        {
            table[h]= n; //setting the first link
            n->next=NULL;
            Number_Of_Words++;
            
        }
        else if (table[h] != NULL) //if it is linked to something else already
        {
            
            n->next = table[h];
            table[h] = n;
            Number_Of_Words++;
            
        }
    }
    fclose(file);
    return true;
}

// Returns number of words in dictionary if loaded else 0 if not yet loaded
unsigned int size(void)
{
    // TODO
    return Number_Of_Words;
}

// Unloads dictionary from memory, returning true if successful else false
bool unload(void)
{
    // TODO
    for (int i = 0; i<N; i++)
    {
        node* cursor = table[i]; //node pointer starts at each index of the array
        while(cursor!=NULL) //to iteratively check each node of the linked list until the end
        {
            node* temp = cursor; //temporary node
            cursor = cursor -> next;// to go to next node
            free(temp);
        }
    }
    return true;  
}
