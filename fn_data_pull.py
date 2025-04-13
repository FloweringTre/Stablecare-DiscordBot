import numpy as np
import mysql.connector
import random
from typing import Any

def connect_db():
    return mysql.connector.connect(
        #Database Values
        
    )

#####################################################################################
################################# SERVER DATA PULLS #################################
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
async def count_servers():
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

### Remove all server related data
async def remove_server_data(server_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        QUERY_HORSE = (f'DELETE FROM horse_information WHERE server_id = {server_id}')
        cursor.execute(QUERY_HORSE)
        QUERY_SERVER = (f'DELETE FROM server_data WHERE server_id = {server_id}')
        cursor.execute(QUERY_SERVER)
        QUERY_USER = (f'DELETE FROM user_data WHERE server_id = {server_id}')
        cursor.execute(QUERY_USER)
        conn.commit()

        conn.close()
        return True
        
    except mysql.Error as e:
        return e

####################################################################################
################################# USER DATA PULLS #################################
### Register a user
async def register_user(user_id, server_id, user_name, starter_horse_name):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        secret_code = await generate_code()

        QUERY = (
            f'INSERT INTO user_data (user_id, server_id, user_name, serial, secret_code, active_name)'
          + f'VALUES ({user_id}, {server_id}, "{user_name}", DEFAULT, "{secret_code}", "{starter_horse_name}")'
        )
        cursor.execute(QUERY)
        conn.commit() #commits the information above to the database to save the addition of information

        conn.close()
        return True

    except mysql.Error as e:
        return e

### Remove all related user data
async def remove_user_data(user_id, server_id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        QUERY_HORSE = (f'DELETE FROM horse_information WHERE user_id = {user_id} AND server_id = {server_id}')
        cursor.execute(QUERY_HORSE)
        QUERY_USER = (f'DELETE FROM user_data WHERE user_id = {user_id} AND server_id = {server_id}')
        cursor.execute(QUERY_USER)
        conn.commit()

        conn.close()
        return True

    except mysql.Error as e:
        return e

### Update User information
async def update_user_data(user_id, server_id, data_column, updated_value):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        #pass whever column you want in and the value you wante changed in the horse information table
        QUERY_STR = (f"UPDATE user_data SET {data_column} = %s WHERE user_id = %s AND server_id = %s")
        
        cursor.execute(QUERY_STR, (updated_value, user_id, server_id))
        conn.commit()

        conn.close()
        return True #pass a successful operation

    except mysql.connector.Error as e: #report errors that occur
        print(f"An error has happened while attempting to update user data: {e}")
        print(f"The bad query: {QUERY_STR}")
        return False #pass as a failed operation

### gathering information for the user
async def gather_user_data(user_id, server_id):
    conn = connect_db()
    cursor = conn.cursor()

    SELECTION_STR = (f'SELECT * FROM user_data WHERE user_id = {user_id} AND server_id = {server_id}')
    cursor.execute(SELECTION_STR)
    user_data = cursor.fetchone()
    
    conn.close()
    
    return user_data

### how many users do we have????
async def count_users():
    conn = connect_db()
    cursor = conn.cursor()

    #fetch a count of the servers
    cursor.execute("SELECT COUNT(*) FROM user_data")
    user_count = cursor.fetchone()
    
    conn.close()
    
    return user_count

### generate the user's secret code
async def generate_code():
    letters = ("A", "B", "C", "D", "E", "F", "G", "H", "J", "K", "M", "N", "P", "Q", "R", "T", "U", "V", "W", "X", "Y", "Z") #length 22
    numbers = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9") #length 10

    code = ""
    for i in range(3): #generate 3 random letters
        val = random.randrange(0, 21)
        code += letters[val]
    
    for i in range(3):  #generate 3 random numbers that are already string values
        val = random.randrange(0, 9)
        code += numbers[val]

    for i in range(3):  #generate 3 random letters
        val = random.randrange(0, 21)
        code += letters[val]
    
    return code

####################################################################################
################################# HORSE DATA PULLS #################################
### register a new horse
async def register_horse(user_id, server_id, user_name, pony_name, pony_sx_int, coat, ref_img : str = ""):
    user_data = await gather_user_data(user_id, server_id)

    if user_data: #user already exists, add another horse to the counter
        if user_data[12] == 15: #check if maxxed out on horse counter
            return "maxxed"
        else:
            await update_user_data(user_id, server_id, "num_horses", 1)

    else: #no user data exists - register them
        await register_user(user_id, server_id, user_name, pony_name)

    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        cust_thumb = 0
        if not(ref_img == ""):
            cust_thumb = 1

        QUERY = (
              f'INSERT INTO horse_information (user_id, server_id, user_name, horse_name, gender, coat, custom_thumb, stand_ref_image, happy_ref_img, sad_ref_img, feed_img, water_img, brush_img, treat_img, pet_img, train_img, show_img, serial)' 
          + f'VALUES ({user_id}, {server_id}, "{user_name}", "{pony_name}", {pony_sx_int}, {coat}, {cust_thumb}, "{ref_img}", "", "", "", "", "", "", "", "", "", DEFAULT);'
        )

        cursor.execute(QUERY)
        conn.commit() #commits the information above to the database to save the addition of information

        ### fetch the horse information that we just registered
        HORSE_QUERY = (
            f'SELECT * FROM horse_information WHERE user_id = {user_id} AND server_id = {server_id} AND horse_name = "{pony_name}" AND gender = {pony_sx_int} AND is_active = 1 '
        )
        cursor.execute(HORSE_QUERY)
        new_horse_data = cursor.fetchone()

        #update the user_data with the active horse serial number
        await update_user_data(user_id, server_id, "active_serial", new_horse_data[25])

        conn.close()
        return True

    except mysql.Error as e:
        return e

### gathering information for the active horse of a specified user
async def gather_all_horse_data(user_id, server_id):
    conn = connect_db()
    cursor = conn.cursor()

    #fetch all data for the ACTIVE horse in the horse information table for the specific user and server
    SELECTION_STR = (f'SELECT * FROM horse_information WHERE user_id = {user_id} AND server_id = {server_id} AND is_active = 1')
    cursor.execute(SELECTION_STR)
    horse_data = cursor.fetchone()
    
    conn.close()
    
    return horse_data

### gathering information for a very specific horse, regardless of server and user
async def get_specific_horse_data(horse_serial):
    conn = connect_db()
    cursor = conn.cursor()

    #fetch all data for the requested horse in the horse information table
    SELECTION_STR = (f'SELECT * FROM horse_information WHERE serial = {horse_serial}')
    cursor.execute(SELECTION_STR)
    horse_data = cursor.fetchone()
    
    conn.close()
    
    return horse_data

### how many horses do we have????
async def count_horses():
    conn = connect_db()
    cursor = conn.cursor()

    #fetch a count of the servers
    cursor.execute("SELECT COUNT(*) FROM horse_information")
    horse_count = cursor.fetchone()
    
    conn.close()
    
    return horse_count

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

### update table information for a horse
async def update_horse_data(user_id, server_id, data_column, updated_value):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        #pass whever column you want in and the value you wante changed in the horse information table
        QUERY_STR = (f"UPDATE horse_information SET {data_column} = %s WHERE user_id = %s AND server_id = %s AND is_active = 1")
        
        cursor.execute(QUERY_STR, (updated_value, user_id, server_id))
        conn.commit()

        conn.close()
        return True #pass a successful operation

    except mysql.connector.Error as e: #report errors that occur
        print(f"An error has happened while attempting to update horse data: {e}")
        print(f"The bad query: {QUERY_STR}")
        return False #pass as a failed operation

### update all table values to reduce horse feed and water stats
async def daily_horse_update():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        ### Randomized stats values done by -> FLOOR([LOW VALUE] + RAND() * [TOP VALUE]) <-
        
        #reduce stat values
        cursor.execute("UPDATE horse_information SET hunger = hunger - FLOOR(1 + RAND() * 5) WHERE is_active = 1")
        cursor.execute("UPDATE horse_information SET thirst = thirst - FLOOR(1 + RAND() * 5) WHERE is_active = 1")
        cursor.execute("UPDATE horse_information SET clean = clean - FLOOR(1 + RAND() * 4) WHERE is_active = 1")
        conn.commit()

        #ensure no stat is below zero
        cursor.execute("UPDATE horse_information SET hunger = 0 WHERE hunger < 0")
        cursor.execute("UPDATE horse_information SET thirst = 0 WHERE thirst < 0")
        cursor.execute("UPDATE horse_information SET clean = 0 WHERE clean < 0")
        conn.commit()

        #update health based on other values
        cursor.execute("UPDATE horse_information SET health = health - FLOOR(1 + RAND() * 3) WHERE hunger <= 5 AND thirst <= 5 AND is_active = 1")
        conn.commit()

        #ensure health is not below zero
        cursor.execute("UPDATE horse_information SET health = 0 WHERE health < 0")
        conn.commit()

        #reset daily training number
        cursor.execute("UPDATE horse_information SET daily_trainings = 0")
        conn.commit()

        cursor.execute("SELECT user_id, server_id FROM horse_information WHERE health > 7 AND health < 10")
        mid_users = cursor.fetchall()

        cursor.execute("SELECT user_id, server_id FROM horse_information WHERE health = 10")
        perf_users = cursor.fetchall()

        
        ##perfect health bonuses
        for U in perf_users:
            QUERY_PERF_1 = f'UPDATE user_data SET money_pts = money_pts + FLOOR(6 + RAND() * 10) WHERE user_id = {U[0]} AND server_id = {U[1]}'
            cursor.execute(QUERY_PERF_1)
            QUERY_PERF_2 = f'UPDATE user_data SET monthly_bot_pts = monthly_bot_pts + FLOOR(6 + RAND() * 12) WHERE user_id = {U[0]} AND server_id = {U[1]}'
            cursor.execute(QUERY_PERF_2)

        #mediocore health bonuses
        for U in mid_users:
            QUERY_MID_1 = f'UPDATE user_data SET money_pts = money_pts + FLOOR(2 + RAND() * 5) WHERE user_id = {U[0]} AND server_id = {U[1]}'
            cursor.execute(QUERY_MID_1)
            QUERY_MID_2 = f'UPDATE user_data SET monthly_bot_pts = monthly_bot_pts + FLOOR(2 + RAND() * 5) WHERE user_id = {U[0]} AND server_id = {U[1]}'
            cursor.execute(QUERY_MID_2)

        conn.close()
        
        servers = await count_servers()
        horses = await count_horses()
        message = servers + horses
        return message #return the number of servers and horses updated

    except mysql.connector.Error as e: #report error
        print(f'An error has happened while attempting to update all horses values: {e}')
        message = ""
        return message #return the error message

### fetch all horses a user owns
async def list_user_horses(user_id, server_id):
    conn = connect_db()
    cursor = conn.cursor()

    #fetch all data for the ACTIVE horse in the horse information table for the specific user and server
    SELECTION_STR = (f'SELECT serial, horse_name, gender, is_active FROM horse_information WHERE user_id = {user_id} AND server_id = {server_id} ORDER BY is_active DESC')
    cursor.execute(SELECTION_STR)
    horse_data = cursor.fetchall()
    
    conn.close()
    
    return horse_data

### Swap active horses
async def horse_swap(user_id, server_id, new_active_id, new_active_name):
    # Change the current active horse to inactive
    await update_horse_data(user_id, server_id, "is_active", 0)

    try:
        conn = connect_db()
        cursor = conn.cursor()

        #set the new active horse
        QUERY_STR = (f"UPDATE horse_information SET is_active = 1 WHERE user_id = %s AND server_id = %s AND serial = %s")
        cursor.execute(QUERY_STR, (user_id, server_id, new_active_id))

        QUERY_2_STR = (f"UPDATE user_data SET active_serial = %s WHERE user_id = %s AND server_id = %s")
        cursor.execute(QUERY_2_STR, (new_active_id, user_id, server_id))

        QUERY_3_STR = (f"UPDATE user_data SET active_name = %s WHERE user_id = %s AND server_id = %s")
        cursor.execute(QUERY_3_STR, (new_active_name, user_id, server_id))

        conn.commit()

        conn.close()
        return True #pass as a successful operation

    except mysql.connector.Error as e: #report errors that occur
        print(f"An error has happened while attempting to update horse data: {e}")
        print(f"The bad query: {QUERY_STR}")
        return False #pass as a failed operation


################################################################################
################################# POINTS PULLS #################################
### get top 5 values
async def get_leaderboard(server_id, point_type):
    conn = connect_db()
    cursor = conn.cursor()

    #fetch the top 5 of a specific leaderboard type sorted largest to smallest
    SELECTION_STR = (f'SELECT user_name, active_name, {point_type}_pts FROM user_data WHERE server_id = {server_id} AND {point_type}_pts > 0 ORDER BY {point_type}_pts DESC')
    cursor.execute(SELECTION_STR)
    leaderboard = cursor.fetchmany(5)
    
    conn.close()
    
    return leaderboard


### Update the point value of a listed player - including money
async def update_user_points(user_id, server_id, point_type, change_value):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        #point types are "money", "server", "champion", "harpg", "monthly_bot", and "lifetime_bot"

        QUERY_STR = (f"UPDATE user_data SET {point_type}_pts = {point_type}_pts + %s WHERE user_id = %s AND server_id = %s")
        
        cursor.execute(QUERY_STR, (change_value, user_id, server_id))
        conn.commit()

        conn.close()
        return True #pass a successful operation

    except mysql.connector.Error as e: #report errors
        print(f"An error has happened while attempting to update {user_id}'s points value in {server_id}: {e}")
        print(f"The bad query: {QUERY_STR}")
        return False #pass as a failed operation


#################################################################################
################################# CUSTOM IMAGES #################################
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


########################################################################################
################################# TRAINING AND SHOWING #################################
### get random question for training/showing
async def get_question(stat_value):
    conn = connect_db()
    cursor = conn.cursor()

    level = 0
    if stat_value >= 0 and stat_value < 11:
        level = 1
    elif stat_value >= 10 and stat_value < 21:
        level = 2
    elif stat_value >= 20 and stat_value < 31:
        level = 3
    elif stat_value >= 30:
        level = 3
    
    if level == 0: #check for a bad value
        return False

    #select a random question from the specified level table
    SELECTION_STR = (f'SELECT * FROM math_questions WHERE level = {level} ORDER BY RAND() LIMIT 1')

    cursor.execute(SELECTION_STR)
    question = cursor.fetchone()
    
    conn.close()
    
    return question

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