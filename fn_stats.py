import numpy as np
import mysql.connector
import random
from typing import Any
import discord

from data_pull import *

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


