#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
typedef uint8_t BYTE;

int main(int argc, char *argv[])
{
    BYTE buffer[512];    //buffer array to store read bytes
    if (argc != 2)
    {
        printf ("Usage ./recover image name\n");
        return 1;
    }


    // creating file pointer to the memory card
    FILE* file = fopen(argv[1], "r");
    //if not a file
    if (file == NULL)
    {
        printf ("Could not open file.\n");
        return 1;
    }


    //to count and use for naming jpgs
    int count = 0;
    //file pointer to the file in which we are writing to
    FILE* img;
    //storing name of jpeg
    char filename[8];
    //while it is not EOF
    while (fread(buffer, sizeof(buffer), 1, file) == 1)
    {
        
        //conditions for jpeg
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
        {   
            //or if img!=null, meaning file already exists
            if (count > 0)
            {
                //close the already open file
                fclose(img);
                //inputting the triple digit names in the array
                sprintf(filename,"%03d.jpg", count);
                count++;
                //opens img for writing
                img = fopen(filename, "w");
                //writing in img from the buffer
                fwrite(buffer, sizeof(buffer), 1, img);
            }
            //or if img==null, or start of first jpeg
            if (count == 0)
            {
                //name outfile using sprintf
                sprintf(filename,"%03d.jpg", count);
                count++;
                //open img for writing
                img = fopen(filename, "w");
                //writing in img from the buffer
                fwrite(buffer, sizeof(buffer), 1, img);
            }
        }
        //for the 512 blocks after the jpeg header
        else if (count > 0)
        {

            fwrite(buffer, sizeof(buffer), 1, img);
        }
    }
    fclose (img); //closing file
    fclose (file); //closing file
    return 0;

}