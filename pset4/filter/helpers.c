#include "helpers.h"
#include <math.h>
#include <stdio.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    float avg = 0;
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            avg += image[i][j].rgbtBlue;
           
            avg += image[i][j].rgbtGreen;
           
            avg += image[i][j].rgbtRed;
         
            avg = round(avg/3.0);
            
            image[i][j].rgbtBlue = avg;
            image[i][j].rgbtGreen = avg;
            image[i][j].rgbtRed = avg;
            avg = 0;
        }
    }
    return;
}

// Convert image to sepia
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    float originalRed, originalGreen, originalBlue;
    float sepiaRed, sepiaGreen, sepiaBlue;
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            originalBlue = image[i][j].rgbtBlue;
            originalGreen = image[i][j].rgbtGreen;
            originalRed = image[i][j].rgbtRed;
            sepiaRed = .393 * originalRed + .769 * originalGreen + .189 * originalBlue;
            int resultR = (int) round(sepiaRed);
            if(resultR>255)
            {
                resultR = 255;
            }
            sepiaGreen = .349 * originalRed + .686 * originalGreen + .168 * originalBlue;
            int resultG = (int) round(sepiaGreen);
            if(resultG>255)
            {
                resultG = 255;
            }
            sepiaBlue = .272 * originalRed + .534 * originalGreen + .131 * originalBlue;
            int resultB = (int) round(sepiaBlue);
            if(resultB>255)
            {
                resultB = 255;
            }
            
            image[i][j].rgbtBlue = resultB;
            image[i][j].rgbtGreen = resultG;
            image[i][j].rgbtRed = resultR;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE original[height][width];
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            original[i][j] = image[i][j];
        }
    }
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j< width; j++)
        {
            int k = width - 1 - j;
            if(j==width/2)
            {
                image[i][j] = image[i][j];
            }
            image[i][j] = original[i][k];
        }
    }
    return;
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    float avgRed, avgGreen, avgBlue;
    RGBTRIPLE orig[height][width];
    for(int i = 0; i < height; i++)
    {
        
        for (int j = 0; j < width; j++)
        {
            orig[i][j] = image[i][j];
        }
    }

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {   
            avgRed = orig[i][j].rgbtRed;
            avgGreen = orig[i][j].rgbtGreen;
            avgBlue = orig[i][j].rgbtBlue;
            int counter = 1;
            if(j - 1 > -1) //possible to add the element to the left
            {
                avgRed+= orig[i][j-1].rgbtRed;
                avgGreen+= orig[i][j-1].rgbtGreen;
                avgBlue+= orig[i][j-1].rgbtBlue;
                counter++;
            }
            if (i - 1 > -1) //possible to add the element above
            {
                avgRed+= orig[i-1][j].rgbtRed;
                avgGreen+= orig[i-1][j].rgbtGreen;
                avgBlue+= orig[i-1][j].rgbtBlue;
                counter++;
            }
            if (j + 1 < width) //possible to add the element to the right
            {
                avgRed+= orig[i][j+1].rgbtRed;
                avgGreen+= orig[i][j+1].rgbtGreen;
                avgBlue+= orig[i][j+1].rgbtBlue;
                counter++;
            }
            if (i + 1 < height) //possible to add the element below
            {
                avgRed+= orig[i+1][j].rgbtRed;
                avgGreen+= orig[i+1][j].rgbtGreen;
                avgBlue+= orig[i+1][j].rgbtBlue;
                counter++;
            }
            if (j - 1 > -1 && i - 1 > -1)  //possible to add the element upper left
            {
                avgRed+= orig[i-1][j-1].rgbtRed;
                avgGreen+= orig[i-1][j-1].rgbtGreen;
                avgBlue+= orig[i-1][j-1].rgbtBlue;
                counter++;
            }
            if (j + 1 < width && i - 1 > -1)  //possible to add the element upper right
            {
                avgRed+= orig[i-1][j+1].rgbtRed;
                avgGreen+= orig[i-1][j+1].rgbtGreen;
                avgBlue+= orig[i-1][j+1].rgbtBlue;
                counter++;
            }
            if (j - 1 > -1 && i + 1 < height)  //possible to add the element bottom left
            {
                avgRed+= orig[i+1][j-1].rgbtRed;
                avgGreen+= orig[i+1][j-1].rgbtGreen;
                avgBlue+= orig[i+1][j-1].rgbtBlue;
                counter++;
            }
            if (j + 1 < width && i + 1 < height) //possible to add the element bottom right
            {
                avgRed+= orig[i+1][j+1].rgbtRed;
                avgGreen+= orig[i+1][j+1].rgbtGreen;
                avgBlue+= orig[i+1][j+1].rgbtBlue;
                counter++;
            }
            avgRed = avgRed/counter;
            avgBlue = avgBlue/counter;
            avgGreen = avgGreen/counter;
            image[i][j].rgbtRed = round(avgRed);
            image[i][j].rgbtBlue = round(avgBlue);
            image[i][j].rgbtGreen = round(avgGreen);
        }
    }
    return;
}