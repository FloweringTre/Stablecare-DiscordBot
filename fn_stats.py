import numpy as np
import mysql.connector
import random
from typing import Any
import discord

from fn_data_pull import *

########################################################################################
################################# STABLECARE FUNCTIONS #################################
### Build the emoji strings for the stat display
async def stat_string(horse_data):
    #Variables to add the discord icons to the strings
    BLANK_SQ = ":black_large_square:"
    HEAL_SQ = ":red_square:"
    HEAL_IC = ":heart:"
    HUN_SQ = ":green_square:"
    HUN_IC = ":green_apple:"
    THIR_SQ = ":blue_square:"
    THIR_IC = ":droplet:"
    CLEN_SQ = ":yellow_square:"
    CLEN_IC = ":sparkles:"

    #Strings for each stat
    health = f"{HEAL_IC} - "
    hunger = f"{HUN_IC} - "
    thirst = f"{THIR_IC} - "
    clean = f"{CLEN_IC} - "

    #loop to add color boxes
    for heal in range(horse_data[5]):
        health += HEAL_SQ
    for hun in range(horse_data[6]):
        hunger += HUN_SQ
    for thir in range(horse_data[7]):
        thirst += THIR_SQ
    for clen in range(horse_data[8]):
        clean += CLEN_SQ
    
    #loop to add black boxes
    for heal in range(10 - horse_data[5]):
        health += BLANK_SQ
    for hun in range(10 - horse_data[6]):
        hunger += BLANK_SQ
    for thir in range(10 - horse_data[7]):
        thirst += BLANK_SQ
    for clen in range(10 - horse_data[8]):
        clean += BLANK_SQ
    
    #finish off strings
    health += " - Health"
    hunger += " - Hunger"
    thirst += " - Thirst"
    clean += " - Cleanliness"

    STAT_STRING = health + f'\n' + hunger + f'\n' + thirst + f'\n' + clean
    return STAT_STRING

### Fetch the URL for the image needed by the activity
async def fetch_image(horse_data, image_type):
    #preset the images to be the standard ref incase something goes wrong
    cust_array_value = 15
    pre_array_value = 2
    
    #find the array location for the image type
    match image_type:
        case 0:
            ## "stand_ref_image"
            cust_array_value = 15
            pre_array_value =  2
        case 1:
            ## "happy_ref_img"
            cust_array_value = 16
            pre_array_value = 3
        case 2:
            ## "sad_ref_img"
            cust_array_value = 17
            pre_array_value = 4
        case 3:
            ## "feed_img"
            cust_array_value = 18
            pre_array_value = 6
        case 4:
            ## "water_img"
            cust_array_value = 19
            pre_array_value = 7
        case 5:
            ## "brush_img"
            cust_array_value = 20
            pre_array_value = 5
        case 6:
            ## "treat_img"
            cust_array_value = 21
            pre_array_value = 8
        case 7:
            ## "pet_img"
            cust_array_value = 22
            pre_array_value = 9
        case 8:
            ## "train_img"
            cust_array_value = 23
            pre_array_value = 10
        case 9:
            ## "show_img"
            cust_array_value = 24
            pre_array_value = 11

    image_url = "" #set up variable

    if horse_data[14] == 1: #custom images are active
        image_url = horse_data[cust_array_value]

        if image_url == "": #if the custom image for that specific value is blank.... 
            image_url = horse_data[15]  #set to the custom standard ref

    else: #preset images are active
        coat_values = await gather_coat_values(horse_data[13])
        image_url = coat_values[pre_array_value]
    
    return image_url
