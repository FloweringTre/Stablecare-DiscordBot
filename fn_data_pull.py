import numpy as np
import mysql.connector
import random
from typing import Any
import discord

def connect_db():
    return mysql.connector.connect(
        #Database Values
             
    )

########################################################################################
################################# STABLECARE FUNCTIONS #################################
### gathering information for the server
async def get_server_data(server_id):
    conn = connect_db()
    cursor = conn.cursor()

    #fetch the data for the specified server
    SELECTION_STR = (f'SELECT * FROM server_data WHERE server_id = {server_id}')
    cursor.execute(SELECTION_STR)
    server_data = cursor.fetchone()
    
    conn.close()
    
    return server_data

### how many servers are we in????
async def count_servers(server_id):
    conn = connect_db()
    cursor = conn.cursor()

    #fetch a count of the servers
    cursor.execute("SELECT COUNT(*) FROM server_data")
    server_count = cursor.fetchone()
    
    conn.close()
    
    return server_count

### updating server information
async def update_server_data(server_id, data_column, updated_value):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        #update specified column withe the specified value
        QUERY_STR = (f"UPDATE server_data SET {data_column} = %s WHERE server_id = %s")
        cursor.execute(QUERY_STR, (updated_value, server_id))
        conn.commit()

        conn.close()
        return True #pass as a successful operation

    except mysql.connector.Error as e: # report error
        print(f"An error has happened while attempting to server update data for {server_id}: {e}")
        print(f"The bad query: {QUERY_STR}")
        return False #pass as a failed operation

### gathering information for the horse
async def gather_all_horse_data(user_id, server_id):
    conn = connect_db()
    cursor = conn.cursor()

    #fetch all data for the horse in the horse information table for the specific user and server
    SELECTION_STR = (f'SELECT * FROM horse_information WHERE user_id = {user_id} AND server_id = {server_id}')
    cursor.execute(SELECTION_STR)
    horse_data = cursor.fetchone()
    
    conn.close()
    
    return horse_data

### gather coat data
async def gather_coat_values(coat_id):
    conn = connect_db()
    cursor = conn.cursor()

    #clean up the coat id value as it comes in with {}
    coat = str(coat_id)
    cleaning_coat = coat.replace("{", "")
    shined_coat = cleaning_coat.replace("}", "")

    #buil the selection string
    SELECTION_STR = (f'SELECT * FROM preset_images WHERE coat_id = ')
    SELECTION_STR += shined_coat

    cursor.execute(SELECTION_STR)
    coat_values = cursor.fetchone()
    
    conn.close()
    
    return coat_values

### get top 5 values
async def get_leaderboard(server_id, point_type):
    conn = connect_db()
    cursor = conn.cursor()

    #fetch the top 5 of a specific leaderboard type sorted largest to smallest
    SELECTION_STR = (f'SELECT user_name, horse_name, {point_type}_pts FROM horse_information WHERE server_id = {server_id} AND {point_type}_pts > 0 ORDER BY {point_type}_pts DESC')
    cursor.execute(SELECTION_STR)
    leaderboard = cursor.fetchmany(5)
    
    conn.close()
    
    return leaderboard

### get random question for training/showing
async def get_question(stat_value):
    conn = connect_db()
    cursor = conn.cursor()

    level = 0
    if stat_value >= 0 or stat_value < 11:
        level = 1
    elif stat_value >= 10 or stat_value < 21:
        level = 2
    elif stat_value >= 20 or stat_value < 31:
        level = 3
    elif stat_value >= 30:
        level = 3
    
    if level == 0: #check for a bad value
        return False

    question_table = f'math_lvl_{level}' #find the level of the table

    #select a random question from the specified level table
    SELECTION_STR = (f'SELECT * FROM {question_table} ORDER BY RAND() LIMIT 1')

    cursor.execute(SELECTION_STR)
    question = cursor.fetchone()
    
    conn.close()
    
    return question

### update table information for a horse
async def update_horse_data(user_id, server_id, data_column, updated_value):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        #pass whever column you want in and the value you wante changed in the horse information table
        QUERY_STR = (f"UPDATE horse_information SET {data_column} = %s WHERE user_id = %s AND server_id = %s")
        
        cursor.execute(QUERY_STR, (updated_value, user_id, server_id))
        conn.commit()

        conn.close()
        return True #pass a successful operation

    except mysql.connector.Error as e: #report errors that occur
        print(f"An error has happened while attempting to update data: {e}")
        print(f"The bad query: {QUERY_STR}")
        return False #pass as a failed operation

### update all table values to reduce horse feed and water stats
async def daily_horse_update():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        ### Randomized stats values done by -> FLOOR([LOW VALUE] + RAND() * [TOP VALUE]) <-
        
        #reduce stat values
        cursor.execute("UPDATE horse_information SET hunger = hunger - FLOOR(1 + RAND() * 5)")
        cursor.execute("UPDATE horse_information SET thirst = thirst - FLOOR(1 + RAND() * 5)")
        cursor.execute("UPDATE horse_information SET clean = clean - FLOOR(1 + RAND() * 4)")
        conn.commit()

        #ensure no stat is below zero
        cursor.execute("UPDATE horse_information SET hunger = 0 WHERE hunger < 0")
        cursor.execute("UPDATE horse_information SET thirst = 0 WHERE thirst < 0")
        cursor.execute("UPDATE horse_information SET clean = 0 WHERE clean < 0")
        conn.commit()

        #update health based on other values
        cursor.execute("UPDATE horse_information SET health = health - FLOOR(1 + RAND() * 3) WHERE hunger <= 5 AND thirst <= 5")
        conn.commit()

        #ensure health is not below zero
        cursor.execute("UPDATE horse_information SET health = 0 WHERE health < 0")
        cursor.execute("UPDATE horse_information SET money = money + FLOOR(2 + RAND() * 5) WHERE health > 7 AND health < 10")
        cursor.execute("UPDATE horse_information SET money = money + FLOOR(6 + RAND() * 10) WHERE health = 10")
        cursor.execute("UPDATE horse_information SET bot_pts = bot_pts + FLOOR(2 + RAND() * 5) WHERE health > 7 AND health < 10")
        cursor.execute("UPDATE horse_information SET bot_pts = bot_pts + FLOOR(6 + RAND() * 12) WHERE health = 10")
        conn.commit()

        #reset daily training number
        cursor.execute("UPDATE horse_information SET daily_trainings = 0")
        conn.commit()

        cursor.execute("SELECT COUNT(*) FROM server_data")
        servers = cursor.fetchone()
        cursor.execute("SELECT COUNT(*) FROM horse_information")
        horses = cursor.fetchone()

        message = servers + horses

        conn.close()
        return message #return the number of servers and horses updated

    except mysql.connector.Error as e: #report error
        print(f'An error has happened while attempting to update all horses values: {e}')
        message = ""
        return message #return the error message

### Update the money of a listed player
async def update_user_money(user_id, server_id, change_value):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        #seperated from points due to how the columns are named.
        QUERY_STR = (f"UPDATE horse_information SET money = money + %s WHERE user_id = %s AND server_id = %s")
        
        cursor.execute(QUERY_STR, (change_value, user_id, server_id))
        conn.commit()

        conn.close()
        return True #pass as a successful operation

    except mysql.connector.Error as e: #report errors
        print(f"An error has happened while attempting to update a player's money: {e}")
        print(f"The bad query: {QUERY_STR}")
        return False #pass as a failed operation

### Update the point value of a listed player
async def update_user_points(user_id, server_id, point_type, change_value):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        #point types are "bot", "server", and "harpg"

        QUERY_STR = (f"UPDATE horse_information SET {point_type}_pts = {point_type}_pts + %s WHERE user_id = %s AND server_id = %s")
        
        cursor.execute(QUERY_STR, (change_value, user_id, server_id))
        conn.commit()

        conn.close()
        return True #pass a successful operation

    except mysql.connector.Error as e: #report errors
        print(f"An error has happened while attempting to update {user_id}'s points value in {server_id}: {e}")
        print(f"The bad query: {QUERY_STR}")
        return False #pass as a failed operation

### Set custom images to use
async def set_custom_image(user_id, server_id, image_type, image_url):
    horse_data = await gather_all_horse_data(user_id, server_id)
    data_column = ""
    match image_type:
        case 0:
            data_column = "stand_ref_image"
        case 1:
            data_column = "happy_ref_img"
        case 2:
            data_column = "sad_ref_img"
        case 3:
            data_column = "feed_img"
        case 4:
            data_column = "water_img"
        case 5:
            data_column = "brush_img"
        case 6:
            data_column = "treat_img"
        case 7:
            data_column = "pet_img"
        case 8:
            data_column = "train_img"
        case 9:
            data_column = "show_img"
        case _:
            data_column = ""

    if data_column == "": #check for a bad image type value
        return False
    
    else: #set the image url
        try:
            conn = connect_db()
            cursor = conn.cursor()

            #update the image url
            QUERY_STR = (f"UPDATE horse_information SET {data_column} = %s WHERE user_id = %s AND server_id = %s")
            cursor.execute(QUERY_STR, (image_url, user_id, server_id))
            conn.commit()
            
            #trigger the custom thumb boolean
            QUERY_CUST = (f"UPDATE horse_information SET custom_thumb = 1 WHERE user_id = %s AND server_id = %s")
            cursor.execute(QUERY_CUST, (user_id, server_id))
            conn.commit()

            conn.close()
            return True #pass as a successful operation

        except mysql.connector.Error as e: #report errors that occurred
            print(f"An error has happened while attempting to update {user_id}'s {data_column} in {server_id}: {e}")
            print(f"The bad image url setting query: {QUERY_STR}")
            print(f"The bad custom thumb bool query: {QUERY_CUST}")
            return False #pass as a failed operation

### Remove custom images to use
async def remove_custom_image(user_id, server_id, image_type):
    #pull the horse's data for cross checking
    horse_data = await gather_all_horse_data(user_id, server_id)
    
    #name variables
    data_column = ""
    array_value = 0
    image_url = "" ## to reset the image URL to a blank value

    #match the incoming image type with its data column name and the column number.
    match image_type:
        case 0:
            data_column = "stand_ref_image"
            array_value = 15 
        case 1:
            data_column = "happy_ref_img"
            array_value = 16
        case 2:
            data_column = "sad_ref_img"
            array_value = 17
        case 3:
            data_column = "feed_img"
            array_value = 18
        case 4:
            data_column = "water_img"
            array_value = 19
        case 5:
            data_column = "brush_img"
            array_value = 20
        case 6:
            data_column = "treat_img"
            array_value = 21
        case 7:
            data_column = "pet_img"
            array_value = 22
        case 8:
            data_column = "train_img"
            array_value = 23
        case 9:
            data_column = "show_img"
            array_value = 24
        case _:
            data_column = ""
            array_value = 0

    #catches for a bad image type number or errors
    if data_column == "":
        return False
    if array_value == 0:
        return False
    
    #catches in cases where you are trying to a remove an image that doesn't exist
    if horse_data[array_value] == "":
        return True
    
    else: #reset the image value
        try:
            conn = connect_db()
            cursor = conn.cursor()

            #reset the image cell value to be blank
            QUERY_STR = (f"UPDATE horse_information SET {data_column} = %s WHERE user_id = %s AND server_id = %s")
            cursor.execute(QUERY_STR, (image_url, user_id, server_id))
            conn.commit()

            custom = False #checking boolean
            for image in range(15,22): # go through the custom image array values and check for images.
                if not(horse_data[image] == ""):
                    if image == array_value: ## if the image we just removed triggers, #noitdidn'tLOL
                        custom = False
                    else: #if the box isnt blank, there are still custom images that trigger here.
                        custom = True

            if not custom: #If there are no custom images.... reset custom tumbnail bool
                QUERY_CUST = (f"UPDATE horse_information SET custom_thumb = 0 WHERE user_id = {user_id} AND server_id = {server_id}")
                cursor.execute(QUERY_CUST)
                conn.commit()

            conn.close()

            return True #This exits the function noting a successful operation

        #report errors that happen while running this function.
        except mysql.connector.Error as e:
            print(f"An error has happened while attempting to remove {user_id}'s {data_column} in {server_id}: {e}")
            print(f"The bad remove image query: {QUERY_STR}")
            print(f"The bad reset custom image bool query: {QUERY_CUST}")
            return False # pass a failed operation

### Update the discipline_level of a user
async def discipline_level(user_id, server_id, horse_data, discipline):
    #name variables
    new_dis_level = 0.0
    sk_1 = 0.0
    sk_2 = 0.0
    sk_3 = 0.0

    match discipline:
        case 0: # Dressage
            sk_1 = horse_data[26] # Balance
            sk_2 = horse_data[29] # Flexibility
            sk_3 = horse_data[27] / 2 # Agility *WEAK
        case 1: # Show Jumping
            sk_1 = horse_data[26] / 2 # Balance *WEAK
            sk_2 = horse_data[28] # Power
            sk_3 = horse_data[27] # Agility
        case 2: # Barrel Racing
            sk_1 = horse_data[28] # Power
            sk_2 = horse_data[29] / 2 # Flexibility *WEAK
            sk_3 = horse_data[27] # Agility
        case 3: # Western Pleasure
            sk_1 = horse_data[26] # Balance
            sk_2 = horse_data[29] # Flexibility
            sk_3 = horse_data[28] / 2 # Power *WEAK
    
    #create the discipline level stat
    new_dis_level = sk_1 + sk_2 + sk_3

    conn = connect_db()
    cursor = conn.cursor()

    #database call to set the discipline level
    QUERY_STR = (f"UPDATE horse_information SET dis_level = %s WHERE user_id = %s AND server_id = %s")
        
    cursor.execute(QUERY_STR, (new_dis_level, user_id, server_id))
    conn.commit()

    conn.close()

### Set the score for the show
async def show_score(user_id, server_id, horse_data, correct):
    dis_level = horse_data[31] #discipline specific score

    #half health points + 1/4 of the sum of the other stats.
    horse_stats = (horse_data[5] / 2) + ((horse_data[6] + horse_data[7] + horse_data[8]) / 4)

    #add a random chance points because shows are unpredictable in their rides.
    additions = random.randrange(0, 2)

    #add a random value of additional points depending on if the user answered the question correctly.
    if correct:
        additions += random.randrange(2, 5)
    else:
        additions += random.randrange(1, 3)
    
    #create the show score for the horse
    show_level = dis_level + additions + horse_stats

    ### Send the show score to the database for storing.
    conn = connect_db()
    cursor = conn.cursor()

    QUERY_STR = (f"UPDATE horse_information SET show_score = %s WHERE user_id = %s AND server_id = %s")
        
    cursor.execute(QUERY_STR, (show_level, user_id, server_id))
    conn.commit()
    conn.close()

### Run the show for the specificed server
async def run_show(server_id):
    conn = connect_db()
    cursor = conn.cursor()

    #Only pull non-zero scores from a specific server - sort data to be largest to smallest
    SELECTION_STR = (f'SELECT user_id, horse_name, show_score FROM horse_information WHERE server_id = {server_id} AND show_score > 0 ORDER BY show_score DESC')
    cursor.execute(SELECTION_STR)
    scoreboard = cursor.fetchmany(8) # fetch top 8
    
    conn.close()
    
    return scoreboard

### Clear all show related scores
async def clear_show_scores(server_id):
    conn = connect_db()
    cursor = conn.cursor()

    score_query = f'UPDATE horse_information SET show_score = 0 WHERE server_id = {server_id}'
    is_query = f'UPDATE horse_information SET is_showing = 0 WHERE server_id = {server_id}'

    cursor.execute(score_query)
    cursor.execute(is_query)
    conn.commit()
    
    conn.close()