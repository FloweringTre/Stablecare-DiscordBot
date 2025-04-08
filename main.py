import discord.member
import numpy as np
import mysql.connector
import random
from typing import Any
import discord
from discord.ext import commands
from discord.ext import tasks
from discord import app_commands

SERVER = 0 #add testing discord server id here
BOT_COLOR = discord.Color.from_str("#81A6EE")

NO_HORSE_ERROR_MESSAGE = f'Sorry, we don\'t have a horse registered to you in our barn. You can get a horse using the \'/createapony\' command.'
NO_SERVER_ERROR_MESSAGE = f'Sorry, your server isn\'t set up with this bot. Please have the server owner run the \'/setup\' command.'
BOT_CREDITS = f'This bot was made in collaboration between kyraltre and MoonFlower. We thank you for using our bot!'


def connect_db():
    return mysql.connector.connect(
        #Database Values
             
    )

#############################################################################
################################# FUNCTIONS #################################
#############################################################################
class Client(commands.Bot):
    async def on_ready(self): #on launch
        print(f'Successfully connected as {self.user}.')
        print("successfully finished startup")
        
        self.stats_update.start()
        print(f'started the stat update loop')

        self.run_the_shows.start()
        print(f'started the show running loop')

        try: #force syncing with the dev server to test commands
            guild=discord.Object(id=SERVER)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to guild {guild.id}')

        except Exception as e: #find errors with the syncing of commands
            print(f'Error syncing commands: {e}')


    ########################################################################################
    ################################# STABLECARE FUNCTIONS #################################
    ### gathering information for the server
    async def get_server_data(server_id):
        conn = connect_db()
        cursor = conn.cursor()

        SELECTION_STR = (f'SELECT * FROM server_data WHERE server_id = {server_id}')
        #print(f'Horse Data Query: {SELECTION_STR}')
        cursor.execute(SELECTION_STR)
        server_data = cursor.fetchone()
        
        conn.close()
        
        return server_data
    
    ### count number of servers the bot is in
    async def count_servers():
        conn = connect_db()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM server_data")
        servers = cursor.fetchone()
        
        conn.close()
        
        return servers

    ### updating server information
    async def update_server_data(server_id, data_column, updated_value):
        try:
            conn = connect_db()
            cursor = conn.cursor()

            QUERY_STR = (f"UPDATE server_data SET {data_column} = %s WHERE server_id = %s")
            
            cursor.execute(QUERY_STR, (updated_value, server_id))
            conn.commit()
            #print(f"The good query: {QUERY_STR}")

            conn.close()
            return True

        except mysql.connector.Error as e:
            print(f"An error has happened while attempting to server update data for {server_id}: {e}")
            print(f"The bad query: {QUERY_STR}")
            return False

    ### gathering information for the horse
    async def gather_all_horse_data(user_id, server_id):
        conn = connect_db()
        cursor = conn.cursor()

        SELECTION_STR = (f'SELECT * FROM horse_information WHERE user_id = {user_id} AND server_id = {server_id}')
        #print(f'Horse Data Query: {SELECTION_STR}')
        cursor.execute(SELECTION_STR)
        horse_data = cursor.fetchone()
        
        conn.close()
        
        return horse_data

    ### gather coat data
    async def gather_coat_values(coat_id):
        conn = connect_db()
        cursor = conn.cursor()

        coat = str(coat_id)
        cleaning_coat = coat.replace("{", "")
        shined_coat = cleaning_coat.replace("}", "")

        SELECTION_STR = (f'SELECT * FROM preset_images WHERE coat_id = ')
        SELECTION_STR += shined_coat

        #print(f'Coat Query: {SELECTION_STR}')
        cursor.execute(SELECTION_STR)
        coat_values = cursor.fetchone()
        
        conn.close()
        
        return coat_values
    
    ### get top 5 values
    async def get_leaderboard(server_id, point_type):
        conn = connect_db()
        cursor = conn.cursor()

        SELECTION_STR = (f'SELECT user_name, horse_name, {point_type}_pts FROM horse_information WHERE server_id = {server_id} AND {point_type}_pts > 0 ORDER BY {point_type}_pts DESC')
        #print(f'Horse Data Query: {SELECTION_STR}')
        cursor.execute(SELECTION_STR)
        leaderboard = cursor.fetchmany(5)
        
        conn.close()
        
        return leaderboard

    ### get random question for training/showing
    async def get_question(question_level):
        conn = connect_db()
        cursor = conn.cursor()

        if (question_level < 0) or (question_level > 3):
            return False

        question_table = f'math_lvl_{question_level}'

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

            QUERY_STR = (f"UPDATE horse_information SET {data_column} = %s WHERE user_id = %s AND server_id = %s")
            
            cursor.execute(QUERY_STR, (updated_value, user_id, server_id))
            conn.commit()
            #print(f"The good query: {QUERY_STR}")

            conn.close()
            return True

        except mysql.connector.Error as e:
            print(f"An error has happened while attempting to update data: {e}")
            print(f"The bad query: {QUERY_STR}")
            return False

    ### update all table values to reduce horse feed and water stats
    async def daily_horse_update():
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            #reduce stat values
            cursor.execute("UPDATE horse_information SET hunger = hunger - 2")
            cursor.execute("UPDATE horse_information SET thirst = thirst - 3")
            cursor.execute("UPDATE horse_information SET clean = clean - 1")
            conn.commit()

            #ensure no stat is below zero
            cursor.execute("UPDATE horse_information SET hunger = 0 WHERE hunger < 0")
            cursor.execute("UPDATE horse_information SET thirst = 0 WHERE thirst < 0")
            cursor.execute("UPDATE horse_information SET clean = 0 WHERE clean < 0")
            conn.commit()

            #update health based on other values
            cursor.execute("UPDATE horse_information SET health = health - 2 WHERE hunger <= 5 AND thirst <= 5")
            conn.commit()

            #ensure health is not below zero
            cursor.execute("UPDATE horse_information SET health = 0 WHERE health < 0")
            cursor.execute("UPDATE horse_information SET money = money + 5 WHERE health > 7 AND health < 10")
            cursor.execute("UPDATE horse_information SET money = money + 10 WHERE health = 10")
            cursor.execute("UPDATE horse_information SET bot_pts = bot_pts + 5 WHERE health > 7 AND health < 10")
            cursor.execute("UPDATE horse_information SET bot_pts = bot_pts + 10 WHERE health = 10")
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
            return message

        except mysql.connector.Error as e:
            print(f'An error has happened while attempting to update all horses values: {e}')
            message = ""
            return message

    ### Update the money of a listed player
    async def update_user_money(user_id, server_id, change_value):
        try:
            conn = connect_db()
            cursor = conn.cursor()

            QUERY_STR = (f"UPDATE horse_information SET money = money + %s WHERE user_id = %s AND server_id = %s")
            
            cursor.execute(QUERY_STR, (change_value, user_id, server_id))
            conn.commit()
            #print(f"The good query: {QUERY_STR}")

            conn.close()
            return True

        except mysql.connector.Error as e:
            print(f"An error has happened while attempting to update a player's money: {e}")
            print(f"The bad query: {QUERY_STR}")
            return False
    
    ### Update the point value of a listed player
    async def update_user_points(user_id, server_id, point_type, change_value):
        try:
            conn = connect_db()
            cursor = conn.cursor()

            QUERY_STR = (f"UPDATE horse_information SET {point_type}_pts = {point_type}_pts + %s WHERE user_id = %s AND server_id = %s")
            
            cursor.execute(QUERY_STR, (change_value, user_id, server_id))
            conn.commit()
            #print(f"The good query: {QUERY_STR}")

            conn.close()
            return True

        except mysql.connector.Error as e:
            print(f"An error has happened while attempting to update {user_id}'s points value in {server_id}: {e}")
            print(f"The bad query: {QUERY_STR}")
            return False

    ### Build the stat icon string
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

    ### Set custom images to use
    async def set_custom_image(user_id, server_id, image_type, image_url):
        horse_data = await Client.gather_all_horse_data(user_id, server_id)
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

        if data_column == "":
            return False
        
        else:
            try:
                conn = connect_db()
                cursor = conn.cursor()

                QUERY_STR = (f"UPDATE horse_information SET {data_column} = %s WHERE user_id = %s AND server_id = %s")
                cursor.execute(QUERY_STR, (image_url, user_id, server_id))
                conn.commit()
                    
                QUERY_CUST = (f"UPDATE horse_information SET custom_thumb = 1 WHERE user_id = %s AND server_id = %s")
                cursor.execute(QUERY_CUST, (user_id, server_id))
                conn.commit()
                #print(f"The good query: {QUERY_CUST}")

                conn.close()
                return True

            except mysql.connector.Error as e:
                print(f"An error has happened while attempting to update {user_id}'s {data_column} in {server_id}: {e}")
                print(f"The bad query: {QUERY_STR}")
                print(f"The bad query: {QUERY_CUST}")
                return False

    ### Remove custom images to use
    async def remove_custom_image(user_id, server_id, image_type):
        horse_data = await Client.gather_all_horse_data(user_id, server_id)
        data_column = ""
        array_value = 0
        image_url = ""
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

        if data_column == "":
            return False
        if array_value == 0:
            return False
        
        if horse_data[array_value] == "":
            return True
        
        else:
            try:
                conn = connect_db()
                cursor = conn.cursor()

                QUERY_STR = (f"UPDATE horse_information SET {data_column} = %s WHERE user_id = %s AND server_id = %s")
                cursor.execute(QUERY_STR, (image_url, user_id, server_id))
                conn.commit()

                custom = False
                #print(horse_data)
                for image in range(15,22):
                    if not(horse_data[image] == ""):
                        if image == array_value:
                            custom = False
                        else:
                            custom = True
                            #print(f'custom image found for {horse_data[3]}')

                if not custom:
                    #print(f'No custom images found for {horse_data[3]}')
                    QUERY_CUST = (f"UPDATE horse_information SET custom_thumb = 0 WHERE user_id = {user_id} AND server_id = {server_id}")
                    cursor.execute(QUERY_CUST)
                    conn.commit()
                    #print(f"The good query: {QUERY_CUST}")
                    

                conn.close()
                return True

            except mysql.connector.Error as e:
                print(f"An error has happened while attempting to remove {user_id}'s {data_column} in {server_id}: {e}")
                print(f"The bad query: {QUERY_STR}")
                print(f"The bad query: {QUERY_CUST}")
                return False

    ### Run the feeding stat updates and embed from the drop down
    async def feed_pony(user_id, server_id, horse_data, selection_str, interaction_channel):
        channel = client.get_channel(interaction_channel)
        
        overfed = False
        food_amount = int(selection_str[0])
        food_total = horse_data[6] + food_amount
        if food_total > 10:
            food_total = 10
            updated_health = horse_data[5] - 2
            if updated_health < 0:
                updated_health = 0
            await Client.update_horse_data(user_id, server_id, "health", updated_health)
            overfed = True

        await Client.update_horse_data(user_id, server_id, "hunger", food_total)                
        if horse_data[6] < 10:
            if overfed:
                await Client.update_user_points(user_id, server_id, "bot", 1)
            else:
                await Client.update_user_points(user_id, server_id, "bot", food_amount)

        message = ""
        if food_total == 10 and overfed == False:
            message = f'{horse_data[3]} enjoys this meal. {PRONOUNS_CAP[horse_data[4],0]} is full and satisfied!'
        elif food_total == 10 and overfed == True:
            message = f'While {horse_data[3]} appreciates the food, {PRONOUNS_LOW[horse_data[4],0]} has been overfed... {PRONOUNS_CAP[horse_data[4],0]} doesn\'t feel great right now.'
        else:
            message = f'{PRONOUNS_CAP[horse_data[4],0]} is munching away, {PRONOUNS_LOW[horse_data[4],0]} appreciates the meal!'
            
        title = f'You feed {horse_data[3]} {selection_str}.'
        embed = discord.Embed(title=title, description=message, color= BOT_COLOR)

        if horse_data[14] == 0:
            coat_values = await Client.gather_coat_values(horse_data[13])
            embed.set_image(url = coat_values[6])
        if horse_data[14] == 1 and not(horse_data[18] == ""):
            embed.set_image(url = horse_data[18])

        footer = ""
        if food_total == 10 and overfed == False:
            footer = f'{horse_data[3]} is no longer hungry!'
        elif food_total == 10 and overfed == True:
            footer = f'{horse_data[3]} has been overfed... {PRONOUNS_LOW[horse_data[4],2]} health has decreased.'
        else:
            footer = f'{horse_data[3]} still wants {10-food_total} lbs of food.'
        embed.set_footer(text=footer)

        full_message = f'###{title} \n\n{message} \n\n-# {footer}'
        await channel.send(embed=embed)

    ### Run the watering stat update and embed from the drop down
    async def water_pony(user_id, server_id, horse_data, selection_str, interaction_channel):
        channel = client.get_channel(interaction_channel)
        
        overwatered = False
        water_amount = int(selection_str[0])
        water_total = horse_data[7] + water_amount
        if water_total > 10:
            water_total = 10
            updated_clean = horse_data[8] - 2
            if updated_clean < 0:
                updated_clean = 0
            await Client.update_horse_data(user_id, server_id, "clean", updated_clean)
            overwatered = True

        await Client.update_horse_data(user_id, server_id, "thirst", water_total)                
        if horse_data[7] < 10:
            if overwatered:
                await Client.update_user_points(user_id, server_id, "bot", 1)
            else:
                await Client.update_user_points(user_id, server_id, "bot", water_amount)

        message = ""
        if water_total == 10 and overwatered == False:
            message = f'{horse_data[3]} takes several glups of water. {PRONOUNS_CAP[horse_data[4],2]} thirst is quenched!'
        elif water_total == 10 and overwatered == True:
            message = f'While {horse_data[3]} appreciates the new water, {PRONOUNS_LOW[horse_data[4],0]} also appreciates the muddy mess the overflowed bucket produces... {PRONOUNS_CAP[horse_data[4],0]} rolls around in the mud happily!'
        else:
            message = f'{PRONOUNS_CAP[horse_data[4],0]} takes a little sip, {PRONOUNS_LOW[horse_data[4],0]} appreciates the new water.'
            
        title = f'You fill {horse_data[3]}\'s water bucket with {selection_str}.'
        embed = discord.Embed(title=title, description=message, color= BOT_COLOR)

        if horse_data[14] == 0:
            coat_values = await Client.gather_coat_values(horse_data[13])
            embed.set_image(url = coat_values[7])
        if horse_data[14] == 1 and not(horse_data[19] == ""):
            embed.set_image(url = horse_data[19])

        footer = ""
        if water_total == 10 and overwatered == False:
            footer = f'{horse_data[3]} is no longer thirsty!'
        elif water_total == 10 and overwatered == True:
            footer = f'{horse_data[3]}\'s waterbucket has overflowed and created a mess... {PRONOUNS_LOW[horse_data[4],2]} cleanliness has decreased.'
        else:
            footer = f'{horse_data[3]} still wants {10-water_total} gallons of water.'
        embed.set_footer(text=footer)

        full_message = f'###{title} \n\n{message} \n\n-# {footer}'
        await channel.send(embed=embed)

    ### Run the health stat update and embed from the drop down
    async def vet_pony(user_id, server_id, horse_data, selection_str, interaction_channel):
        channel = client.get_channel(interaction_channel)
        
        overhealth = False
        health_amount = int(selection_str[0])
        
        health_total = horse_data[5] + health_amount
        if health_total > 10:
            health_total = 10
            overhealth = True

        await Client.update_horse_data(user_id, server_id, "health", health_total)                
        if horse_data[5] < 10:
            if overhealth:
                await Client.update_user_points(user_id, server_id, "bot", 1)
            else:
                await Client.update_user_points(user_id, server_id, "bot", health_amount)

        message = ""
        if overhealth:
            match health_amount:
                case 1:
                    message = f'The vet performs a wellness check on {horse_data[3]}. They find nothing wrong with {PRONOUNS_LOW[horse_data[4],1]}'
                case 2:
                    message = f'The vet double checks their paperwork... and finds {horse_data[3]} doesn\'t need any vaccines right now. They still perform a once over on {horse_data[3]}, just to verify {PRONOUNS_LOW[horse_data[4],0]} is in good health.'
                case 3:
                    message = f'The vet checks {horse_data[3]}\'s sample, and really doesn\'t need deworming right now. They still issue a minimal dose to remove the tiny amount that do exist, but warns that over-worming can cause resistance to the treatment.'
                case 4:
                    message = f'The vet performs the body work on {horse_data[3]}... but finds that {horse_data[3]} is loose and limber already.'
                case 5:
                    message = f'The vet sedates and starts work on {horse_data[3]}]\'s mouth... but doesn\'t find a lot of work to do. {PRONOUNS_CAP[horse_data[4],1]} mouth looks really good already.'
        else:
            match health_amount:
                case 1:
                    message = f'The vet performs a wellness check on {horse_data[3]}. They find that {horse_data[3]} is stiff, they teach you a series of stretches to do with {horse_data[3]}.'
                case 2:
                    message = f'The vet gives {horse_data[3]} {PRONOUNS_LOW[horse_data[4],1]} vaccines. {PRONOUNS_CAP[horse_data[4],0]} stands and is very brave for {PRONOUNS_LOW[horse_data[4],1]} shots!'
                case 3:
                    message = f'The vet checks {horse_data[3]}\'s sample and finds worms! They immediately administer dewormer to {horse_data[3]}. {PRONOUNS_CAP[horse_data[4],0]} willingly takes the medicine.'
                case 4:
                    message = f'The vet performs body work on {horse_data[3]}. Through the process, {horse_data[3]} becomes more comfortable, loose, and limber.'
                case 5:
                    message = f'The vet sedates and floats {horse_data[3]}\'s teeth. The sharp points are smoothed and {horse_data[3]} has a pain free mouth.'

        if health_total == 10 and overhealth == False:
            message += f'\n\n{horse_data[3]} overjoyed that the vet came by. {PRONOUNS_CAP[horse_data[4],0]} is feeling so much better now!'
        elif health_total == 10 and overhealth == True:
            message += f'\n\nWhile {horse_data[3]} appreciates the care from the vet, {PRONOUNS_LOW[horse_data[4],0]} is just fine... The vet is also mildly upset they were called out for no reason.'
        else:
            message += f'\n\n{horse_data[3]} is happy the vet is here to help {PRONOUNS_LOW[horse_data[4],1]}.'
         

        title = f'The vet has visited {horse_data[3]}.'
        embed = discord.Embed(title=title, description=message, color= BOT_COLOR)

        footer = ""
        if health_total == 10 and overhealth == False:
            footer = f'{horse_data[3]} is at full health!'
        elif health_total == 10 and overhealth == True:
            footer = f'{horse_data[3]} had vet work done to {PRONOUNS_LOW[horse_data[4],1]} that {PRONOUNS_LOW[horse_data[4],0]} didn\'t need. {PRONOUNS_CAP[horse_data[4],0]} is sad.'
        else:
            footer = f'{horse_data[3]} still needs to regain {10-health_total} health points.'
        embed.set_footer(text=footer)

        full_message = f'###{title} \n\n{message} \n\n-# {footer}'
        await channel.send(embed=embed)

    ### Run the clean stat update and embed from the drop down
    async def groom_pony(user_id, server_id, horse_data, selection_str, interaction_channel):
        channel = client.get_channel(interaction_channel)
        
        overclean = False
        clean_amount = int(selection_str[0])
        
        clean_total = horse_data[8] + clean_amount
        if clean_total > 10:
            clean_total = 10
            overclean = True

        await Client.update_horse_data(user_id, server_id, "clean", clean_total)                
        if horse_data[8] < 10:
            await Client.update_user_points(user_id, server_id, "bot", clean_amount)

        message = ""
        match clean_amount:
            case 1:
                message = f'{horse_data[3]} leans into you while you lightly brush {PRONOUNS_LOW[horse_data[4],1]}. You can feel the love. :heart:'
            case 2:
                message = f'You throughly clean {horse_data[3]}. {PRONOUNS_CAP[horse_data[4],0]} loves every moment of the process.'
            case 3:
                message = f'While {horse_data[3]} struggles to stand still for the braiding, you eventually finish putting {PRONOUNS_LOW[horse_data[4],2]} hair into the protective styles.'
            case 4:
                message = f'You spend the afternoon bathing {horse_data[3]}. {PRONOUNS_CAP[horse_data[4],0]} now is sparkling and beautiful.'

        if clean_total == 10 and overclean == False:
            message += f'\n\n{horse_data[3]} is looking perfect! {PRONOUNS_CAP[horse_data[4],0]} is completely clean!'
        elif clean_total == 10 and overclean == True:
            message += f'\n\nWhile {horse_data[3]} appreciates the care and attention, but {PRONOUNS_LOW[horse_data[4],0]} is now thinking of ways to get dirty since they have been overly pampered.'
        else:
            message += f'\n\n{horse_data[3]} is happy to be getting this attention!.'

        title = f'You have groomed {horse_data[3]}.'
        embed = discord.Embed(title=title, description=message, color= BOT_COLOR)

        if horse_data[14] == 0:
            coat_values = await Client.gather_coat_values(horse_data[13])
            embed.set_image(url = coat_values[5])
        if horse_data[14] == 1 and not(horse_data[20] == ""):
             embed.set_image(url = horse_data[20])

        footer = ""
        if clean_total == 10:
            footer = f'{horse_data[3]} is completely clean!'
        else:
            footer = f'{horse_data[3]} still needs to regain {10-clean_total} clean points.'
        embed.set_footer(text=footer)

        full_message = f'###{title} \n\n{message} \n\n-# {footer}'
        await channel.send(embed=embed)

    ### Run the treat embed from the drop down
    async def treat_pony(user_id, server_id, horse_data, selection_str, interaction_channel):
        channel = client.get_channel(interaction_channel)
        
        treat_low = selection_str.lower()
        message = f'{PRONOUNS_CAP[horse_data[4], 0]} happily takes the {treat_low} from you. {horse_data[3]} loves it and nickers happily at you!'
        
        title = f'You give {horse_data[3]} a {selection_str}.'
        embed = discord.Embed(title=title, description=message, color= BOT_COLOR)

        if horse_data[14] == 0:
            coat_values = await Client.gather_coat_values(horse_data[13])
            embed.set_image(url = coat_values[8])
        if horse_data[14] == 1 and not(horse_data[21] == ""):
             embed.set_image(url = horse_data[21])
        
        await channel.send(embed=embed)

    ### Update the discipline_level of a user
    async def discipline_level(user_id, server_id, horse_data, discipline):
        # Disciplines:
        ### 0 - Dressage -- balance_sk / flex_sk / agility_sk
        ### 1 - Show Jumping -- balance_sk / power_sk / agility_sk
        ### 2 - Barrel Racing -- power_sk / flex_sk / agility_sk
        ### 3 - Western Pleasure -- balance_sk / flex_sk / power_sk
        conn = connect_db()
        cursor = conn.cursor()

        new_dis_level = 0.0
        sk_1 = 0.0
        sk_2 = 0.0
        sk_3 = 0.0

        match discipline:
            case 0:
                sk_1 = horse_data[26] / 10
                sk_2 = horse_data[29] / 10
                sk_3 = horse_data[27] / 10
            case 1:
                sk_1 = horse_data[26] / 10
                sk_2 = horse_data[28] / 10
                sk_3 = horse_data[27] / 10
            case 2:
                sk_1 = horse_data[28] / 10
                sk_2 = horse_data[29] / 10
                sk_3 = horse_data[27] / 10
            case 3:
                sk_1 = horse_data[26] / 10
                sk_2 = horse_data[29] / 10
                sk_3 = horse_data[28] / 10
        
        new_dis_level = sk_1 + sk_2 + sk_3

        QUERY_STR = (f"UPDATE horse_information SET dis_level = %s WHERE user_id = %s AND server_id = %s")
            
        cursor.execute(QUERY_STR, (new_dis_level, user_id, server_id))
        conn.commit()
            #print(f"The good query: {QUERY_STR}")

        conn.close()

    ### Set the score for the show
    async def show_score(user_id, server_id, horse_data, correct):
        conn = connect_db()
        cursor = conn.cursor()

        dis_level = horse_data[31]
        additions = random.randrange(0, 2)
        if correct:
            additions += random.randrange(2, 5)
        else:
            additions += random.randrange(1, 3)
        
        show_level = dis_level + additions

        QUERY_STR = (f"UPDATE horse_information SET show_score = %s WHERE user_id = %s AND server_id = %s")
            
        cursor.execute(QUERY_STR, (show_level, user_id, server_id))
        conn.commit()
            #print(f"The good query: {QUERY_STR}")

        conn.close()

    ### Run the shows
    async def run_show(server_id, discipline):
        conn = connect_db()
        cursor = conn.cursor()

        SELECTION_STR = (f'SELECT user_id, horse_name, show_score FROM horse_information WHERE server_id = {server_id} AND show_score > 0 AND discipline = {discipline} ORDER BY show_score DESC')
        #print(f'Horse Data Query: {SELECTION_STR}')
        cursor.execute(SELECTION_STR)
        scoreboard = cursor.fetchmany(8)
        
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


####################################################################################################
################################# UPDATE HORSE STATS EVERY 12 HOURS #################################
    @tasks.loop(hours=12)
    async def stats_update(self):
        result = await Client.daily_horse_update()
        console_message = ""

        if result == "":
            console_message = (f'An error occurred while trying to run the update to all horse stats.')

        else:
            #print(result)
            console_message = (f'The stats of {result[1]} horses have been successfully updated across {result[0]} servers.')
         
        print(console_message)

        counter = 0        
        try:
            for guild in client.guilds:
                counter += 1
                server_id = guild.id
                server_data = await Client.get_server_data(server_id)
                for channel in guild.channels:
                    if channel.id == server_data[4]:
                        role = guild.get_role(server_data[3])
                        message = f'{role.mention} - Stats have been updated.'
                        await channel.send(f'{message}', allowed_mentions=discord.AllowedMentions(roles=True))
                    elif channel.id == server_data[5]:
                        role = guild.get_role(server_data[6])
                        message = f'Hello {role.mention}! The barn has been updated and your horses would like some attention!'
                        await channel.send(f'{message}', allowed_mentions=discord.AllowedMentions(roles=True))
    
        except:
            server_count = await Client.count_servers()
            print(f'Aparently there was an error sending messages about the horse update....')
            print(f'Messages sent in {counter} out of {server_count[0]} servers.')
        
    @stats_update.before_loop
    async def before_my_task(self):
            await self.wait_until_ready()

####################################################################################################
################################# RUN HORSE SHOWS EVERY 24 HOURS #################################
    @tasks.loop(hours=24)
    async def run_the_shows(self):
        servers = client.guilds
        counter = 0
        try:
            for guild in servers:
                counter += 1
                server_id = guild.id
                server_data = await Client.get_server_data(server_id)
                channel = guild.get_channel(server_data[5])

                dressage = await Client.run_show(server_id, 0)
                jumping = await Client.run_show(server_id, 1)
                rodeo = await Client.run_show(server_id, 2)
                pleasure = await Client.run_show(server_id, 3)

                title = ":trophy: Daily Horse Show Results! :trophy:"
                content = f'Congratulations to all the winners of our daily show!\n'
                embed = discord.Embed(title=title, description=content, color= BOT_COLOR)

                shows_ran = 0
                show = ""

                show_pts = [0, 24, 21, 18, 15, 12, 9, 6, 3]
                show_money = [0, 15, 12, 9, 6, 3, 2, 1, 1]

                if dressage:
                    placement = 1
                    shows_ran += 1
                    show = "Dressage"
                    message = ""

                    for L in dressage:
                        user_name = await client.fetch_user(L[0])
                        message += f'{placement}. {user_name.mention} and {L[1]} - {L[2]} pts\n'
                        await Client.update_user_money(L[0], server_id, show_money[placement])
                        await Client.update_user_points(L[0], server_id, "server", show_pts[placement])
                        placement += 1
                    embed.add_field(name=":gem: Dressage :gem:", value=message)
                
                if jumping:
                    placement = 1
                    shows_ran += 1
                    show = "Show Jumping"
                    message = ""

                    for L in jumping:
                        user_name = await client.fetch_user(L[0])
                        message += f'{placement}. {user_name.mention} and {L[1]} - {L[2]} pts\n'
                        await Client.update_user_money(L[0], server_id, show_money[placement])
                        await Client.update_user_points(L[0], server_id, "server", show_pts[placement]) 
                        placement += 1
                    embed.add_field(name=":wing: Show Jumping :wing:", value=message)
                
                if rodeo:
                    placement = 1
                    shows_ran += 1
                    show = "Barrel Racing"
                    message = ""

                    for L in rodeo:
                        user_name = await client.fetch_user(L[0])
                        message += f'{placement}. {user_name.mention} and {L[1]} - {L[2]} pts\n'
                        await Client.update_user_money(L[0], server_id, show_money[placement])
                        await Client.update_user_points(L[0], server_id, "server", show_pts[placement]) 
                        placement += 1
                    embed.add_field(name=":racehorse: Barrel Racing :racehorse:", value=message)

                if pleasure:
                    placement = 1
                    shows_ran += 1
                    show = "Western Pleasure"
                    message = ""

                    for L in pleasure:
                        user_name = await client.fetch_user(L[0])
                        message += f'{placement}. {user_name.mention} and {L[1]} - {L[2]} pts\n'
                        await Client.update_user_money(L[0], server_id, show_money[placement])
                        await Client.update_user_points(L[0], server_id, "server", show_pts[placement]) 
                        placement += 1
                    embed.add_field(name=":carousel_horse: Western Pleasure :carousel_horse:", value=message)
                
                embed.set_footer(text=BOT_CREDITS)
                
                next_show_val = random.randrange(0, 3)
                next_show = ""
                match next_show_val:
                    case 0:
                        next_show = "Dressage"
                    case 1:
                        next_show = "Show Jumping"
                    case 2:
                        next_show = "Barrel Racing"
                    case 3:
                        next_show = "Western Pleasure"
                        
                await Client.update_server_data(server_id, "daily_dis_class", next_show_val)

                show_title = f':rosette: Today\'s Show - {next_show} :rosette:'
                show_message = f'Enter today\'s {next_show} using the \'/entershow\' command. If your horse isn\'t registered as a {next_show} horse, use the \'setdiscipline\' command!'
                embed.add_field(name= show_title, value= show_message, inline=False)

                for channel in guild.channels:
                    if channel.id == server_data[4]: #admin
                        role = guild.get_role(server_data[3])
                        if shows_ran > 0:
                            message = f'{role.mention} - A {show} show has been run in your server.'
                        else:
                            message = f'No shows were run in your server. There were no entries yesterday.'
                        await channel.send(f'{message}', allowed_mentions=discord.AllowedMentions(roles=True))
                    elif channel.id == server_data[5]: #to players
                        role = guild.get_role(server_data[6])
                        message = f'There was no entries for yesterday\'s show... if you want to enter today\'s {next_show} show, use \'/entershow\' '
                        if shows_ran > 0:
                            await channel.send(embed=embed, allowed_mentions=discord.AllowedMentions(roles=True))
                        else:
                            await channel.send(message)
                    else:
                        pass
                    
                await Client.clear_show_scores(server_id)
                print(f'completed show run for {server_data[1]}')
        except:
            server_count = await Client.count_servers()
            print(f'Aparently there was an error running the shows....')
            print(f'Shows ran in {counter} out of {server_count[0]} servers.')
        
        
    @run_the_shows.before_loop
    async def before_my_task(self):
            await self.wait_until_ready()


###################################################################################
################################# BOT SET UP CODE #################################
###################################################################################

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents) #prefixes are outdated however still required in the call functions

GUILD_ID = discord.Object(id=SERVER) 
#commands are not globally used as it takes 1+hrs to actually get to all discord servers when globally triggered

##################################################################################
################################# SLASH COMMANDS #################################
##################################################################################
# this is for slash commands, names of commands have to be lower case
# descriptions can have upper case

########################################################################################
################################# INFORMATION COMMANDS #################################
### help on user commands
@client.tree.command(name="helpinformation", description="Get information on the StableCare bot", guild=GUILD_ID)
async def informationMessage(interaction: discord.Interaction):
    server_data = await Client.get_server_data(interaction.guild.id)
    horse_data = await Client.gather_all_horse_data(interaction.user.id, interaction.guild.id)
    message = ""
    title = ""
    if horse_data:
        #if the player has a horse
        var1 = str(PRONOUNS_LOW[horse_data[4],[2]])
        var2 = var1.replace("['", "")
        hpronoun = var2.replace("']", "")

        title = f'Information about the StableCare Bot!'
        message = (f'Here are the commands available to help you interact with your horse, {horse_data[3]}. ') 
        
        embed = discord.Embed(title= title, description=message, color= BOT_COLOR)
            
        check_t = (f':horse: **Check in on your horse and see {hpronoun} stats.** :horse:')
        check_m = (f' /checkonpony\n')
        feed_t = (f':green_apple: **Improve {horse_data[3]}\'s hunger stat** :green_apple:' ) 
        feed_m = (f' /feed\n' )  
        water_t = (f':droplet: **Improve {horse_data[3]}\'s thirst stat** :droplet:' ) 
        water_m = (f' /water\n') 
        brush_t = (f':sparkles: **Improve {horse_data[3]}\'s cleanliness stat** :sparkles:' ) 
        brush_m = (f' /groom\n') 
        vet_t = (f':heart: **Improve {horse_data[3]}\'s health stat** :heart:' ) 
        vet_m = (f' /vetcare\n' ) 
        treat_t = (f':candy: **Give {horse_data[3]} a treat** :candy:' ) 
        treat_m = (f' /treats\n' ) 
                
        point_t = (f':rosette: **Give your horse HARPG points.** :rosette:' ) 
        point_m = (f' /harpgpoints - Allow StableCare to help track your HARPG points for {horse_data[3]}\n' )
        lead_t = (f':trophy: **Check out the server leaderboard** :trophy:' ) 
        lead_m = (f' /leaderboard - You can see the leaderboard for either the Server Points or for  StableCare\'s Care Points\n' )
                   
        image_t = (f':camera_with_flash: **Set custom images for {horse_data[3]}.** :camera_with_flash:' ) 
        image_m = (f' /customimages - List what custom image you want to add and then the image URL. \nGet additional help and info in /helpcustomimages\n' )

        data_t = (f':scissors: **Remove your data with the bot** :scissors:' ) 
        data_m = (f' /removedata - This will erase all stored data associated with your account. \nRequires a \'YES\' for confirmation.\n')
            
        embed.add_field(name= check_t,value= check_m, inline=False)
        embed.add_field(name= feed_t,value= feed_m, inline=False)
        embed.add_field(name= water_t,value= water_m, inline=False)
        embed.add_field(name= brush_t,value= brush_m, inline=False)
        embed.add_field(name= vet_t,value= vet_m, inline=False)
        embed.add_field(name= treat_t,value= treat_m, inline=False)
        embed.add_field(name= point_t,value= point_m, inline=False)
        embed.add_field(name= lead_t,value= lead_m, inline=False)
        embed.add_field(name= image_t,value= image_m, inline=False)
        embed.add_field(name= data_t,value= data_m, inline=False)

    else:
        title = f'Welcome to the StableCare Bot!'
        message = (f'We are thankful that you choose to come to our barn!')

        embed = discord.Embed(title= title, description=message, color= BOT_COLOR)

        about_t = f':heart: **About the StableCare Bot** :heart:'
        about_m = (
            f' This bot (currently) uses slash commands to operate a cute tamagatchi like game where users can have a horse and perform care tasks on it.'
            + f'\nCustom images can be set for the horse and users can use StableCare to track HARPG points. Server moderators can use StableCare to give out server related points.' 
            + f'\n\nThe StableCare bot only requires the permission to send and manage messages.\n'
        )
        

        create_t = f':horse: **Bring a new horse home!** :horse:'
        create_m = f' /createapony - Set your new horse\'s name and gender (0-Mare, 1-Stallion, 2-Gelding)\n'

        data_t = f':scissors: **We value your data!** :scissors:'
        data_m = f'Not only will we never share your data, we also have a built in command to remove all your data at any time. Use \'/removedata\' to erase your data from our bot.\n'
        
        embed.add_field(name= about_t,value= about_m, inline=False)
        embed.add_field(name= create_t,value= create_m, inline=False)
        embed.add_field(name= data_t,value= data_m, inline=False)
    
    
    embed.set_footer(text=BOT_CREDITS)

    channel = interaction.guild.get_channel(server_data[5])
    if not(interaction.channel_id == server_data[5]):
        await interaction.response.send_message(f'I sent the response to your request in the StableCare bot channel :horse::heart: - {channel.mention}', ephemeral= True)
    await channel.send(embed=embed)

### help on the admin specific commands
@client.tree.command(name="helpinformationadmin", description="Admin - Information for the server moderators for this bot.", guild=GUILD_ID)
async def admininformation(interaction: discord.Interaction):
    server_id = interaction.guild.id
    server_data = await Client.get_server_data(server_id)

    user_roles = interaction.user.roles
    admin_found = False

    if server_data:
        for role in user_roles:
            if role.id == server_data[3]:
                admin_found = True
                log_channel = client.get_channel(server_data[4])
                
                title = f'Moderator Information for StableCare'
                message = (
                    f'Each users can have one horse per server.' + f'\n' +
                    f'Horses will need to have their stats cared for using the slash commands and the related drop down menus that populate. The stats for the horse will drop every 12 hours automatically. You should be notified when these updates occur.' + f'\n' +
                    
                    f'\nThese are the moderator specific commands you have for this bot!'
                           )
                
                embed = discord.Embed(title=title, description=message, color=BOT_COLOR)
                
                #embed.add_field(name="", value="", inline=False)
                embed.add_field(name=":horse: Register a Horse for a User :horse:", value="You can run the /createaponyadmin command to register a horse for a user.", inline=False)
                embed.add_field(name=":camera_with_flash: Set/Remove Custom Image for a User :camera_with_flash:", value="You can run the /customimagesadmin command to add or update a custom image associated with a user's account. The '/removeimagesadmin' command will erase all custom images for a user. You see more information in /helpcustomimages.\n", inline=False)
                embed.add_field(name=":scissors: Remove a User's Data :scissors:", value="If you need to remove the data of any user in your server, you can do so with the '/removedatauseradmin' command. It will require two confirmations.\n", inline=False)
                embed.add_field(name=":coin: Give Users Server Points :coin:", value="You can run the /serverpointsadmin command to add (or subtract by using a negative value) points to a user's account. You can use these however you want within your server.\n", inline=False)
                embed.add_field(name=":dollar: Give Users Server Money :dollar:", value="By running the '/servermoneyadmin' command, you can add (or subtract using a negative value) to a user's account. Right now server money has no purpose.\n", inline=False)
                embed.add_field(name=":books: Update Server Information :books:", value="You can update the roles and channels used by the bot by running the '/updateserveradmin' command. You don't have to update all of the values when this command is run.\n", inline=False)
                embed.add_field(name=":wastebasket: Removing the Bot and Data :wastebasket:", value="To remove the bot and erase all user data, first have a user with the Bot Moderation Role run the '/removedataserveradmin' command and complete the three confirmations for removal. After a confirmation of data removal has been set to the Logging Channel, you can safely kick the bot from your server.\n", inline=False)
                
                embed.set_footer(text=BOT_CREDITS)
                
                await log_channel.send(embed=embed)

                if not (interaction.channel_id == log_channel):
                    await interaction.response.send_message(f'This help message has been sent in the log channel for you!', ephemeral = True)
        
        if not admin_found:
            await interaction.response.send_message(f'This command needs to be run by a StableCare Barn Manager. Sorry about that!', ephemeral = True)

    else:
            await interaction.response.send_message(NO_SERVER_ERROR_MESSAGE, ephemeral = True)

### help  on custom images
@client.tree.command(name="helpcustomimages", description="Get information on how to use custom images", guild=GUILD_ID)
async def informationPhotos(interaction: discord.Interaction):
    about_message = (
            f'You have the option to set your own custom images for your horse. To set a custom image for one of the interactions, use the \'/customimages\' command.'+
            f'\n\nImages must be given in URL format. These urls must be the exact URL for just the image, not a webpage the image is on.\n'
    )
    
    updates_message = (       
            f'To update an image, use the \'/customimages\' command like you did to set the original image.\n'
    )
    
    remove_message = (
        f'To remove an image, user the \'/removeimages\' command. You only need to select an image type to remove.\n'
    )

    image_message = ( 
            f'There are 9 different types of custom images you can set. For \'image_type\', enter one of the following options.'+
            f'\n0 - Standard reference image' + 
            f'\n1 - Happy reference image (pefect stats)' + 
            f'\n2 - Sad reference image (low stats)' + 
            f'\n3 - Eating interaction image' + 
            f'\n4 - Drinking interaction image' + 
            f'\n5 - Brushing interaction image' + 
            f'\n6 - Treat feeding interaction image\n' +
            f'\n7 - Petting interaction image\n' +
            f'\n8 - Training image\n' +
            f'\n9 - Competition/Show image\n' 
    )
    where_message = (
        f'If you have set any custom image, they will completely override the use of the preset images. It is recommended to start with the standard reference image so that your checkin with your pony will have an image.\n'
    )

    title = "Using Custom Images with StableCare"
    embed = discord.Embed(title= title, description=about_message, color= BOT_COLOR)
    embed.add_field(name=":camera_with_flash: Updating Images :camera_with_flash:", value=updates_message, inline=False)
    embed.add_field(name=":scissors: Removing Images :scissors:", value=remove_message, inline=False)
    embed.add_field(name=":dividers: Custom Image Types :dividers:", value=image_message, inline=False)
    embed.add_field(name=":question: Where did the check in picture go? :question:", value=where_message, inline=False)
    embed.set_footer(text=BOT_CREDITS)
    
    server_data = await Client.get_server_data(interaction.guild.id)
    channel = interaction.guild.get_channel(server_data[5])
    if not(interaction.channel_id == server_data[5]):
        await interaction.response.send_message(f'I sent the response to your request in the StableCare bot channel :horse::heart: - {channel.mention}', ephemeral= True)
    await channel.send(embed=embed)

### help on the showing and training
@client.tree.command(name="helptraining", description="Get information about training your pony.", guild=GUILD_ID)
async def informationTraining(interaction: discord.Interaction):
    title = f':horse_racing: About Horse Training :horse_racing:'
    about_message = f'We have 4 different skills to train your horse in, **Balance, Flexibility, Power, and Agility**.\nTrain your pony with the \'/trainpony\' command and enter the skill you want to train.'

    embed = discord.Embed(title= title, description=about_message, color= BOT_COLOR)

    embed.add_field(name=":chart_with_upwards_trend: Leveling up :chart_with_upwards_trend:", value="Take your pony out for a ride and brush off your math facts. Answer a math question to level up your pony!", inline=False)
    embed.add_field(name=":books: Math? ToT :books:", value="The math questions are middle school level and have whole number answers. If you get it wrong, there will be a help guide for the next round. There is also no time limit to answer the question.", inline=False)
    embed.add_field(name=":zzz: Not all at once :zzz:", value="Your pony can only go on 3 training sessions every barn update. They need breaks, and so do you!", inline=False)
    embed.add_field(name=":medal: Maxxed skills :medal:", value="Champions practice daily, and so should you! Ponies with maxxed skills can still train in the maxxed skills.", inline=False)

    embed.set_footer(text=BOT_CREDITS)
    
    server_data = await Client.get_server_data(interaction.guild.id)
    channel = interaction.guild.get_channel(server_data[5])
    if not(interaction.channel_id == server_data[5]):
        await interaction.response.send_message(f'I sent the response to your request in the StableCare bot channel :horse::heart: - {channel.mention}', ephemeral= True)
    await channel.send(embed=embed)

@client.tree.command(name="helpshowing", description="Get information about showing your pony.", guild=GUILD_ID)
async def informationShowing(interaction: discord.Interaction):
    title = f':trophy: About Horse Showing :trophy:'
    about_message = (
        f'We have 4 different disciplines to show your horse in, **Dressage, Show Jumping, Barrel Racing, and Western Pleasure**.' +
        f'\nEnter your pony in the daily show with the \'/entershow\' command.' +
        f'\n**Entering a show will consume one training session.** If you have already used all three training sessions, you have to wait for the barn update to register for the show.'
    )

    embed = discord.Embed(title= title, description=about_message, color= BOT_COLOR)

    dss_message = (
        f'**Here are the skills that each discipline need.**'+
        f'\n**Dressage** - Balance, Flexibility, and Agility'+
        f'\n**Show Jumping** - Balance, Agility, and Power'+
        f'\n**Barrel Racing** - Flexibility, Agility, and Power'+
        f'\n**Western Pleasure** - Balance, Flexibility, and Power'
    )

    embed.add_field(name=":books: Disicipline Specific Skills :books:", value=dss_message, inline=False)
    embed.add_field(name=":diamond_shape_with_a_dot_inside: Discipline Scores :diamond_shape_with_a_dot_inside:", value="Your pony's skills points related to the discipline are added together to make up the discipline score. This creates the foundation of your show score.", inline=False)
    embed.add_field(name=":arrows_clockwise: Changing Disciplines :arrows_clockwise:", value="You can change the discipline your pony is registered to at any time with the \'/setdiscipline\' command.", inline=False)
    embed.add_field(name=":calendar_spiral: Daily Shows :calendar_spiral:", value="Each day (24hrs) a new show will start. It is a random chance what discipline is selected for the daily class.", inline=False)
    embed.add_field(name=":rosette: Show Scores :rosette:", value="You will answer a math question to try and get a boost to your discipline score for your show score. There are two random values that are also added in to give each show a bit of :sparkles: *spice* :sparkles:", inline=False)
    embed.add_field(name=":coin: Show Rewards :coin:", value="The top 8 of each show get not only server points but also server money (currently no use).", inline=False)
    

    embed.set_footer(text=BOT_CREDITS)
    
    server_data = await Client.get_server_data(interaction.guild.id)
    channel = interaction.guild.get_channel(server_data[5])
    if not(interaction.channel_id == server_data[5]):
        await interaction.response.send_message(f'I sent the response to your request in the StableCare bot channel :horse::heart: - {channel.mention}', ephemeral= True)
    await channel.send(embed=embed)

###########################################################################################################
################################# BUILD THE BOT - BOT SET UP AND UPDATING #################################
@client.tree.command(name="setup", description="Admin - Set up the StableCare bot for your server!", guild=GUILD_ID)
@app_commands.checks.has_permissions(administrator = True)
async def setupStableCare(interaction: discord.Interaction, moderation_role: str, logging_channel: str, interaction_role: str, interaction_channel: str):
    server_id = interaction.guild_id
    server_name = interaction.guild.name
    user_name = interaction.user.display_name

    bot_moderation_role_id = int(moderation_role.replace("<@&", "").replace(">", ""))
    bot_logging_channel_id = int(logging_channel.replace("<#", "").replace(">", ""))
    bot_interaction_role_id = int(interaction_role.replace("<@&", "").replace(">", ""))
    bot_interaction_channel_id = int(interaction_channel.replace("<#", "").replace(">", ""))

    log_channel = client.get_channel(bot_logging_channel_id)

    server_data = await Client.get_server_data(server_id)

    if server_data:
        log_channel = client.get_channel(server_data[4])
        await log_channel.send(f'{user_name} attempted to run the setup command for this bot... but we are already set up in this server. :horse: :heart:')
        await interaction.response.send_message(f'This bot is already set up in this server. You don\'t have to set it up again.', ephemeral = True)

    else:
        try:
            conn = connect_db() 
            cursor = conn.cursor()
            QUERY = (f"INSERT INTO server_data VALUES ({server_id}, \"{server_name}\", \"{user_name}\", {bot_moderation_role_id}, {bot_logging_channel_id}, {bot_interaction_channel_id}, {bot_interaction_role_id})")
            print(f'Query = {QUERY}')
            cursor.execute(QUERY)
            conn.commit()
            await interaction.response.send_message(f'Thank you for setting up the StableCare bot for this server. Your memebers can now use the \'/createapony\' command to get a horse!')
            await log_channel.send(f'{user_name} set up the StableCare bot for this server. Find out about the admin commands in \'/helpinformationadmin\'')
            
        except mysql.connector.Error as e:
            print(f'{user_name} had issues setting up the bot in {server_name} - {server_id}: {e}') 
            await log_channel.send(f'An error occurred while attempting to set up the bot. If this happens twice, please contact kyraltre.')

        conn.close()

@setupStableCare.error
async def setupErorr(interaction: discord.Interaction, error):
    server_id = interaction.guild_id
    server_data = await Client.get_server_data(server_id)

    if server_data:
        log_channel = client.get_channel(server_data[4])
        log_channel.send(f'{interaction.user.display_name} attempted to run the Setup command for this server.')

    message = f'Sorry, this command has to be run by a server admistrator.' 
    await interaction.response.send_message(message)

### help command for how to set up the bot
@client.tree.command(name="helpsetup", description="How to set up the bot for your server", guild=GUILD_ID)
async def setupHelp(interaction: discord.Interaction):
    title = f'***Welcome to the StableCare bot!***'
    message = (f'In order to set up this bot, the server owner will need to run the \'/setup\' command.' + "\n\n"
               f'This bot needs the following things to operate correctly.'
               )
    embed = discord.Embed(title=title, description=message, color=BOT_COLOR)

    embed.add_field(name="Moderation Role", value="This role is used for giving server specific points, registering horses for others, giving users money, and other elevated bot commands. This role needs no permissions, it is just a tag for the bot to use to ensure the commands are not abused.", inline= False)
    embed.add_field(name="Logging Channel", value="This channel is where the bot will send logs of horses that are registered, user data that is cleared for the server, and other moderation values. It can be a shared log channel with other bots.", inline= False)
    embed.add_field(name="Interaction Role", value="This role is used by the bot to tag players when the stats update.", inline= False)
    embed.add_field(name="Interaction Channel", value="This channel is where the bot will send message and accept slash commands from users.", inline= False)
    

    embed.set_footer(text=BOT_CREDITS)

    await interaction.response.send_message(embed=embed)

### update server data values
@client.tree.command(name="updateserveradmin", description="Admin - Update server data for this bot.", guild=GUILD_ID)
async def updateServer(interaction: discord.Interaction, moderation_role: str = "0", logging_channel: str = "0", interaction_role: str = "0", interaction_channel: str = "0"):
    server_id = interaction.guild.id
    server_data = await Client.get_server_data(server_id)
    user_name = interaction.user.display_name
    user_roles = interaction.user.roles
    admin_found = False

    bot_moderation_role_id = int(moderation_role.replace("<@&", "").replace(">", ""))
    bot_logging_channel_id = int(logging_channel.replace("<#", "").replace(">", ""))
    bot_interaction_role_id = int(interaction_role.replace("<@&", "").replace(">", ""))
    bot_interaction_channel_id = int(interaction_channel.replace("<#", "").replace(">", ""))

    if server_data:
        for role in user_roles:
            if role.id == server_data[3]:
                admin_found = True
                log_channel = client.get_channel(server_data[4])
                changes = 0

                log_message = f'Update server information command has been run.'

                if bot_moderation_role_id > 0:
                    changes += 1
                    result = await Client.update_server_data(server_id, "admin_role_id", bot_moderation_role_id)
                    role_name = interaction.guild.get_role(bot_moderation_role_id)
                    if result:
                        log_message += (f'\n{user_name} ran the server update command - The moderation role has been updated to {role_name.mention}.')
                    else:
                        log_message += (f'\n{user_name} ATTEMPTED to update the server\'s bot admin role to the {role_name.mention}, but something went wrong. If this issue repeats, please contact kyraltre.')

                if bot_interaction_role_id > 0:
                    changes += 1
                    result = await Client.update_server_data(server_id, "interact_role_id", bot_interaction_role_id)
                    role_name = interaction.guild.get_role(bot_interaction_role_id)
                    if result:
                        log_message += (f'\n{user_name} ran the server update command - The interaction role has been updated to {role_name.mention}.')
                    else:
                        log_message += (f'\n{user_name} ATTEMPTED to update the server\'s bot interaction role to the {role_name.mention}, but something went wrong. If this issue repeats, please contact kyraltre.')

                if bot_interaction_channel_id > 0:
                    changes += 1
                    result = await Client.update_server_data(server_id, "interact_channel", bot_interaction_channel_id)
                    if result:
                        log_message += (f'\n{user_name} ran the server update command - The interaction channel was changed to the <#{bot_interaction_channel_id}> channel.')
                    else:
                        log_message += (f'\n{user_name} ATTEMPTED to update the server\'s bot interaction channel, but something went wrong. If this issue repeats, please contact kyraltre.')
                
                if bot_logging_channel_id > 0:
                    changes += 1
                    result = await Client.update_server_data(server_id, "log_channel", bot_logging_channel_id)
                    new_log_channel = client.get_channel(bot_logging_channel_id)
                    if result:
                        log_message += (f'\n{user_name} ran the server update command - The logging channel was changed, this will be the last log message sent in this channel.')
                        await new_log_channel.send(f'{user_name} ran the server update command. This is the new logging channel for this bot.')
                    else:
                        log_message += (f'\n{user_name} ATTEMPTED to update the server\'s bot logging channel, but something went wrong. If this issue repeats, please contact kyraltre.')

                if changes == 0:
                    log_message += (f'\n{user_name} ran the server update command - Nothing was changed.')          

                await log_channel.send(log_message)


        if not admin_found:
            await log_channel.send(f'{user_name} attempted to update the server settings for this bot.')
            await interaction.response.send_message(f'This command needs to be run by a StableCare Barn Manager. Sorry about that!', ephemeral = True)

    else:
        await interaction.response.send_message(NO_SERVER_ERROR_MESSAGE, ephemeral = True)
    

####################################################################################
################################# REMOVE USER DATA #################################
### remove your own data command
@client.tree.command(name="removedata", description="Removes allyour data from this bot - type YES to remove your data", guild=GUILD_ID)
async def removeUserData(interaction: discord.Interaction, confirmation_to_remove_data: str):
    server_id = interaction.guild.id
    user_id = interaction.user.id
    user_name = interaction.user.display_name

    server_id = interaction.guild.id
    server_data = await Client.get_server_data(server_id)
    horse_data = await Client.gather_all_horse_data(user_id, server_id)
    log_channel = client.get_channel(server_data[4])

    if server_data:
        if horse_data:
            if confirmation_to_remove_data == "YES":
                try:
                    conn = connect_db()
                    cursor = conn.cursor()
                    
                    QUERY = (f'DELETE FROM horse_information WHERE user_id = {user_id} AND server_id = {server_id}')
                    cursor.execute(QUERY)
                    conn.commit()

                    conn.close()

                    print(f'Successfully deleted {user_name}\'s data from the {interaction.guild.name} server ({server_id})')
                    await interaction.response.send_message(f'Your data has been successfully removed from this bot. Thank you for your time with us. :heart:', ephemeral = True)
                    await log_channel.send(f'{user_name} has removed their data from the bot for this server.')
                
                except mysql.Error as e:
                    print(f'An error occurred while trying to remove {user_name}\'s data the {interaction.guild.name} server ({server_id}): {e}')
                    await log_channel.send(f'An error has occurred while attempting to remove {user_name}\'s data for this serve. If this repeats, please contact kyraltre.')
                    await interaction.response.send_message(f'An error occurred while trying to delete your data. If this issue repeats, please contact kyraltre. Thank you.', ephemeral = True)

            else:
                await interaction.response.send_message(f'Confirmation not recieved, if you want to remove your data from this bot. Type \'YES\' in the confirmation field', ephemeral = True)
        else:
            await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral = True)
    else:
        await interaction.response.send_message(NO_SERVER_ERROR_MESSAGE, ephemeral = True)

### remove a user's data - admin command
@client.tree.command(name="removedatauseradmin", description="Admin - remove data for a user from this bot that is connected to this server.", guild=GUILD_ID)
async def removeUserDataAdmin(interaction: discord.Interaction, confirmation_to_remove_data: str, user_to_remove: str, confirm_server_id: str):
    server_id = interaction.guild.id
    server_name = interaction.guild.name

    confirmation_server_id = int(confirm_server_id)
    user_id = int(user_to_remove.replace("<@", "").replace(">", ""))

    user_name = await client.fetch_user(user_id)
    admin_name = interaction.user.display_name
    user_roles = interaction.user.roles

    server_data = await Client.get_server_data(server_id)
    log_channel = client.get_channel(server_data[4])
    admin_found = False

    if server_data:
        for role in user_roles:
            if role.id == server_data[3]:
                admin_found = True
                if confirmation_to_remove_data == "YES":
                    if confirmation_server_id == server_id:
                        try:
                            conn = connect_db()
                            cursor = conn.cursor()
                            
                            QUERY_HORSE = (f'DELETE FROM horse_information WHERE user_id = {user_id} AND server_id = {server_id}')
                            cursor.execute(QUERY_HORSE)
                            conn.commit()
                            conn.close()
                            print(f'Successfully deleted {user_name}\'s data from the {server_name} server ({server_id}) -- Request completed by {admin_name} - {interaction.user.id}')
                            await interaction.response.send_message(f'All data for {user_name} related to this server has been removed from the bot.', ephemeral = True)
                            await log_channel.send(f'{admin_name} has removed {user_name}\'s data related to this server from the bot.')
                        
                        except mysql.Error as e:
                            print(f'An error occurred while {admin_name} was trying to remove {user_name}\'s data the {server_name} server ({server_id}): {e}')
                            await log_channel.send(f'An error has occurred while {user_name} was attempting to remove {user_name}\'s data for this server. If this repeats, please contact kyraltre.')
                            await interaction.response.send_message(f'An error occurred while trying to delete {user_name}\'s data. If this issue repeats, please contact kyraltre. Thank you.', ephemeral = True)
                    else:
                        await log_channel.send(f'{admin_name} attempted to remove {user_name}\'s data from this server. Request denied due to mismatched Server ID')
                        await interaction.response.send_message(f'Server ID does not match. Request denied.', ephemeral = True)
                else:
                    await log_channel.send(f'{admin_name} attempted to remove {user_name}\'s data from this server. Request denied due to confirmation not recieved.')
                    await interaction.response.send_message(f'Confirmation not recieved, if you want to remove your data from this bot. Type \'YES\' in the confirmation field', ephemeral = True)

        if not admin_found:
            await log_channel.send(f'{admin_name} attempted to remove {user_name}\'s data from this server. Request denied due to not having bot moderator role.')
            await interaction.response.send_message(f'Request denied. You don\'t have the appropriate role to run this command.', ephemeral = True)
    else:
        await interaction.response.send_message(NO_SERVER_ERROR_MESSAGE, ephemeral = True)

### remove all data for a server
@client.tree.command(name="removedataserveradmin", description="Admin - Removes ALL data for ALL USERS from this bot that is connected to this server.", guild=GUILD_ID)
async def removeServerData(interaction: discord.Interaction, confirmation_to_remove_data: str, confirm_your_user_id: str, confirm_server_id: str):
    server_id = interaction.guild.id
    server_name = interaction.guild.name
    user_id = interaction.user.id
    user_name = interaction.user.display_name
    user_roles = interaction.user.roles

    confirmation_your_user_id = int(confirm_your_user_id) 
    confirmation_server_id = int(confirm_server_id)

    server_data = await Client.get_server_data(server_id)
    log_channel = client.get_channel(server_data[4])
    admin_found = False

    if server_data:
        for role in user_roles:
            if role.id == server_data[3]:
                admin_found = True
                if confirmation_to_remove_data == "YES":
                    if confirmation_your_user_id == user_id:
                        if confirmation_server_id == server_id:
                            try:
                                conn = connect_db()
                                cursor = conn.cursor()
                                
                                QUERY_HORSE = (f'DELETE FROM horse_information WHERE server_id = {server_id}')
                                cursor.execute(QUERY_HORSE)
                                QUERY_SERVER = (f'DELETE FROM server_data WHERE server_id = {server_id}')
                                cursor.execute(QUERY_SERVER)
                                conn.commit()

                                conn.close()

                                print(f'Successfully deleted ALL USER DATA from the {server_name} server ({server_id} -- Request completed by {user_name} - {user_id})')
                                await interaction.response.send_message(f'All data related to this server has been removed from the bot. You are save to remove this bot from your server. Thank you for spending time with us! :heart:', ephemeral = True)
                                await log_channel.send(f'{user_name} has removed ALL DATA related to this server from the bot. You are save to remove this bot from your server. Thank you for spending time with us! :heart:')
                            
                            except mysql.Error as e:
                                print(f'An error occurred while {user_name} was trying to remove ALL USER data the {server_name} server ({server_id}): {e}')
                                await log_channel.send(f'An error has occurred while {user_name} was attempting to remove ALL user data for this server. If this repeats, please contact kyraltre.')
                                await interaction.response.send_message(f'An error occurred while trying to delete ALL user data. If this issue repeats, please contact kyraltre. Thank you.', ephemeral = True)
                        else:
                            await log_channel.send(f'{user_name} attempted to remove ALL user data from this server. Request denied due to mismatched Server ID')
                            await interaction.response.send_message(f'Server ID does not match. Request denied.', ephemeral = True)
                    else:
                        await log_channel.send(f'{user_name} attempted to remove ALL user data from this server. Request denied due to mismatched User ID')
                        await interaction.response.send_message(f'User ID does not match. Request denied.', ephemeral = True)
                else:
                    await log_channel.send(f'{user_name} attempted to remove ALL user data from this server. Request denied due to confirmation not recieved.')
                    await interaction.response.send_message(f'Confirmation not recieved, if you want to remove your data from this bot. Type \'YES\' in the confirmation field', ephemeral = True)

        if not admin_found:
            await log_channel.send(f'{user_name} attempted to remove ALL user data from this server. Request denied due to not having bot moderator role.')
            await interaction.response.send_message(f'Request denied. You don\'t have the appropriate role to run this command.', ephemeral = True)
    else:
        await interaction.response.send_message(NO_SERVER_ERROR_MESSAGE, ephemeral = True)

####################################################################################
################################# SET CUSTOM IMAGES ################################
### set a custom image for any image interaction
@client.tree.command(name="customimages", description="Set a custom image for your horse. See /helpcustomimages for assistance.", guild=GUILD_ID)
async def setCustomImage(interaction: discord.Interaction, image_type: int, image_url: str):
    server_id = interaction.guild.id
    user_id = interaction.user.id
    user_name = interaction.user.display_name

    server_id = interaction.guild.id
    server_data = await Client.get_server_data(server_id)
    horse_data = await Client.gather_all_horse_data(user_id, server_id)
    log_channel = client.get_channel(server_data[4])

    image_name = ""

    match image_type:
            case 0:
                image_name = "standard reference image"
            case 1:
                image_name = "happy reference image"
            case 2:
                image_name = "sad reference image"
            case 3:
                image_name = "eating interaction image"
            case 4:
                image_name = "drinking interaction image"
            case 5:
                image_name = "brushing interaction image"
            case 6:
                image_name = "treat interaction image"
            case 7:
                image_name = "pet interaction image"
            case 8:
                image_name = "training image"
            case 9:
                image_name = "show image"

    if server_data:
        if horse_data:
            if not(image_name == ""):
                results = await Client.set_custom_image(user_id, server_id, image_type, image_url)

                if results:
                    if image_url == "":
                        await interaction.response.send_message(f'{horse_data[2]}\'s {image_name} has been cleared.', ephemeral = True)
                        await log_channel.send(f'{user_name} has removed a custom image from their horse.')
                
                    else:
                        await interaction.response.send_message(f'{horse_data[2]}\'s {image_name} has been updated.', ephemeral = True)
                        await log_channel.send(f'{user_name} has added a custom image to their horse.')
                
                else:
                    print(f'An error occurred while trying to update an image for {user_name} in the {interaction.guild.name} server ({server_id})')
                    await log_channel.send(f'An error has occurred while attempting to update an image for {user_name} for this server. If this repeats, please contact kyraltre.')
                    await interaction.response.send_message(f'An error occurred while trying to update custom images for you. If this issue repeats, please contact kyraltre. Thank you.', ephemeral = True)

            else:
                await interaction.response.send_message(f'Please select an appropriate image type. See /helpcustomimages for assistance.', ephemeral = True)
        else:
            await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral = True)
    else:
        await interaction.response.send_message(NO_SERVER_ERROR_MESSAGE, ephemeral = True)

###admin version of set custom images
@client.tree.command(name="customimagesadmin", description="Admin - Set a custom image for another user", guild=GUILD_ID)
async def setCustomImageAdmin(interaction: discord.Interaction, updating_user: str, image_type: int, image_url: str):
    server_id = interaction.guild.id
    server_name = interaction.guild.name
    user_id = int(updating_user.replace("<@", "").replace(">", ""))

    user_name = await client.fetch_user(user_id)
    admin_name = interaction.user.display_name
    user_roles = interaction.user.roles

    server_data = await Client.get_server_data(server_id)
    log_channel = client.get_channel(server_data[4])
    admin_found = False

    image_name = "a"

    match image_type:
            case 0:
                image_name = "standard reference image"
            case 1:
                image_name = "happy reference image"
            case 2:
                image_name = "sad reference image"
            case 3:
                image_name = "eating interaction image"
            case 4:
                image_name = "drinking interaction image"
            case 5:
                image_name = "brushing interaction image"
            case 6:
                image_name = "treat interaction image"
            case 7:
                image_name = "pet interaction image"
            case 8:
                image_name = "training image"
            case 9:
                image_name = "show image"

    if server_data:
        for role in user_roles:
            if role.id == server_data[3]:
                admin_found = True
                if not(image_name == ""):
                    results = await Client.set_custom_image(user_id, server_id, image_type, image_url)

                    if results:
                        if image_url == "":
                            await interaction.response.send_message(f'{user_name}\'s {image_name} has been cleared.', ephemeral = True)
                            await log_channel.send(f'{admin_name} has removed a custom image from {user_name}\'s horse.')
                    
                        else:
                            await interaction.response.send_message(f'{user_name}\'s {image_name} has been updated.', ephemeral = True)
                            await log_channel.send(f'{admin_name} has added a custom image to {user_name}\'s horse.')
                
                    else:
                        print(f'An error occurred while trying to update an image for {user_name} in the {server_name} server ({server_id})')
                        await log_channel.send(f'An error has occurred while {admin_name} was attempting to update an image for {user_name} for this server. If this repeats, please contact kyraltre.')
                        await interaction.response.send_message(f'An error occurred while trying to update custom images for {user_name}. If this issue repeats, please contact kyraltre. Thank you.', ephemeral = True)

                else:
                    await interaction.response.send_message(f'Please select an appropriate image type. See /helpcustomimages for assistance.', ephemeral = True)
                        
        if not admin_found:
            await log_channel.send(f'{admin_name} attempted to update a custom image for {user_name} . Request denied due to not having bot moderator role.')
            await interaction.response.send_message(f'Request denied. You don\'t have the appropriate role to run this command.', ephemeral = True)
    else:
        await interaction.response.send_message(NO_SERVER_ERROR_MESSAGE, ephemeral = True)

### user remove custom image
@client.tree.command(name="removeimages", description="REMOVE a custom image for your horse. See /helpcustomimages for assistance.", guild=GUILD_ID)
async def setCustomImage(interaction: discord.Interaction, image_type: int):
    server_id = interaction.guild.id
    user_id = interaction.user.id
    user_name = interaction.user.display_name

    server_id = interaction.guild.id
    server_data = await Client.get_server_data(server_id)
    horse_data = await Client.gather_all_horse_data(user_id, server_id)
    log_channel = client.get_channel(server_data[4])

    image_name = ""

    match image_type:
            case 0:
                image_name = "standard reference image"
            case 1:
                image_name = "happy reference image"
            case 2:
                image_name = "sad reference image"
            case 3:
                image_name = "eating interaction image"
            case 4:
                image_name = "drinking interaction image"
            case 5:
                image_name = "brushing interaction image"
            case 6:
                image_name = "treat interaction image"
            case 7:
                image_name = "pet interaction image"
            case 8:
                image_name = "training image"
            case 9:
                image_name = "show image"

    if server_data:
        if horse_data:
            if not(image_name == ""):
                results = await Client.remove_custom_image(user_id, server_id, image_type)

                if results:
                    await interaction.response.send_message(f'{horse_data[2]}\'s {image_name} has been cleared.', ephemeral = True)
                    await log_channel.send(f'{user_name} has removed a custom image from their horse.')
                
                else:
                    print(f'An error occurred while trying to remove an image for {user_name} in the {interaction.guild.name} server ({server_id})')
                    await log_channel.send(f'An error has occurred while attempting to remove an image for {user_name} for this server. If this repeats, please contact kyraltre.')
                    await interaction.response.send_message(f'An error occurred while trying to remove custom images for you. If this issue repeats, please contact kyraltre. Thank you.', ephemeral = True)

            else:
                await interaction.response.send_message(f'Please select an appropriate image type. See /helpcustomimages for assistance.', ephemeral = True)
        else:
            await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral = True)
    else:
        await interaction.response.send_message(NO_SERVER_ERROR_MESSAGE, ephemeral = True)

###admin version of remove custom images
@client.tree.command(name="removeimagesadmin", description="Admin - REMOVE ALL custom images for another user", guild=GUILD_ID)
async def setCustomImageAdmin(interaction: discord.Interaction, updating_user: str):
    server_id = interaction.guild.id
    server_name = interaction.guild.name
    user_id = int(updating_user.replace("<@", "").replace(">", ""))

    user_name = await client.fetch_user(user_id)
    admin_name = interaction.user.display_name
    user_roles = interaction.user.roles

    server_data = await Client.get_server_data(server_id)
    log_channel = client.get_channel(server_data[4])
    admin_found = False

    if server_data:
        for role in user_roles:
            if role.id == server_data[3]:
                admin_found = True
                total = 0
                for image in range(0,9):
                    results = await Client.remove_custom_image(user_id, server_id, image)
                    if results:
                        total +=1
                            
                if total == 9:
                    await interaction.response.send_message(f'ALL of {user_name}\'s custom images have been removed.', ephemeral = True)
                    await log_channel.send(f'{admin_name} has has removed ALL custom images belonging to {user_name}\'s horse.')
                else:
                    print(f'An error occurred while trying remove all images for {user_name} in the {server_name} server ({server_id})')
                    await log_channel.send(f'An error has occurred while {admin_name} was attempting to remove all images for {user_name} for this server. Only {total} out of a possible 9 images have been cleared. If this repeats, please contact kyraltre.')
                    await interaction.response.send_message(f'An error occurred while trying to remove all custom images for {user_name}. Only {total} out of a possible 9 images have been cleared. If this issue repeats, please contact kyraltre. Thank you.', ephemeral = True)

                
                        
        if not admin_found:
            await log_channel.send(f'{admin_name} attempted to update a custom image for {user_name} . Request denied due to not having bot moderator role.')
            await interaction.response.send_message(f'Request denied. You don\'t have the appropriate role to run this command.', ephemeral = True)
    else:
        await interaction.response.send_message(NO_SERVER_ERROR_MESSAGE, ephemeral = True)


#############################################################################################
################################# Point assignment commands #################################
#############################################################################################
### user can add harpg points as they see fit.
@client.tree.command(name="harpgpoints", description="Add HARPG points to your horse. Only accepts whole number values.", guild=GUILD_ID)
async def harpgPoints(interaction: discord.Interaction, points_to_add: int):
    server_id = interaction.guild.id
    user_id = interaction.user.id
    horse_data = await Client.gather_all_horse_data(user_id, server_id)
    message = ""

    if horse_data:
        result = await Client.update_user_points(user_id, server_id, "harpg", points_to_add)
        if result:
            horse_data = await Client.gather_all_horse_data(user_id, server_id)
            message = f'{horse_data[2]}\'s HARPG point total is now {horse_data[12]}'
            
        else:
            message = f'An error occurred while trying to update {horse_data[2]}\'s HARPG points. If this error repeats, please contact kyraltre.'

        await interaction.response.send_message(message, ephemeral = True)
    else:
        await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral = True)

### admin to add server specific points
@client.tree.command(name="serverpointsadmin", description="Admin - Add server points to a user's horse. A negative value will subtract points.", guild=GUILD_ID)
async def serverPoints(interaction: discord.Interaction, updating_user: str, points_to_add: int):
    server_id = interaction.guild.id
    user_id = int(updating_user.replace("<@", "").replace(">", ""))
    user_name = await client.fetch_user(user_id)
    admin_name = interaction.user.display_name
    user_roles = interaction.user.roles

    horse_data = await Client.gather_all_horse_data(user_id, server_id)
    server_data = await Client.get_server_data(server_id)
    log_channel = client.get_channel(server_data[4])
    admin_found = False
    message = ""
    log_message = ""

    if server_data:
        for role in user_roles:
            if role.id == server_data[3]:
                admin_found = True
                if horse_data:
                    result = await Client.update_user_points(user_id, server_id, "server", points_to_add)
                    if result:
                        horse_data = await Client.gather_all_horse_data(user_id, server_id)
                        message = f'{horse_data[2]}, {user_name}\'s horse, server point total is now {horse_data[11]}'
                        log_message = f'{admin_name}, added {points_to_add} server points to {user_name}\'s horse.'

                    else:
                        message = f'An error occurred while trying to update {user_name}\'s server points for {horse_data[2]}. If this error repeats, please contact kyraltre.'
                        log_message = f'{admin_name} ATTEMPTED to add {points_to_add} server points to {user_name}\'s horse but an error occurred.'
                    
                    await log_channel.send(log_message)
                    await interaction.response.send_message(message, ephemeral = True)

                else:
                    await interaction.response.send_message(f'There is no horse registered to {user_name} in this server.', ephemeral = True)
    else:
        await interaction.response.send_message(NO_SERVER_ERROR_MESSAGE, ephemeral = True)

### admin to add money to a user
@client.tree.command(name="servermoneyadmin", description="Admin - Add money to a user's account. A negative value will subtract money.", guild=GUILD_ID)
async def serverMoney(interaction: discord.Interaction, updating_user: str, money_to_add: int):
    server_id = interaction.guild.id
    user_id = int(updating_user.replace("<@", "").replace(">", ""))
    user_name = await client.fetch_user(user_id)
    admin_name = interaction.user.display_name
    user_roles = interaction.user.roles

    horse_data = await Client.gather_all_horse_data(user_id, server_id)
    server_data = await Client.get_server_data(server_id)
    log_channel = client.get_channel(server_data[4])
    admin_found = False
    message = ""
    log_message = ""

    if server_data:
        for role in user_roles:
            if role.id == server_data[3]:
                admin_found = True
                if horse_data:
                    result = await Client.update_user_money(user_id, server_id, money_to_add)
                    if result:
                        horse_data = await Client.gather_all_horse_data(user_id, server_id)
                        message = f'{user_name}\'s account now has ${horse_data[9]}'
                        log_message = f'{admin_name}, added ${money_to_add} to {user_name}\'s account.'

                    else:
                        message = f'An error occurred while trying to update {user_name}\'s money for {horse_data[2]}. If this error repeats, please contact kyraltre.'
                        log_message = f'{admin_name} ATTEMPTED to add ${money_to_add} to {user_name}\'s account but an error occurred.'
                    
                    await log_channel.send(log_message)
                    await interaction.response.send_message(message, ephemeral = True)

                else:
                    await interaction.response.send_message(f'There is no horse registered to {user_name} in this server.', ephemeral = True)
    else:
        await interaction.response.send_message(NO_SERVER_ERROR_MESSAGE, ephemeral = True)

### check out the leaderboard for bot or server points
@client.tree.command(name="leaderboard", description="See the top 5 users and horses for either Care points (0) or Server points (1)", guild=GUILD_ID)
async def leaderboard(interaction: discord.Interaction, leaderboard_type: int):
    server_id = interaction.guild.id
    board = ""
    nice_type = ""
    title = ""
    message = ""
    match leaderboard_type:
        case 0:
            board = "bot"
            nice_type = "Care Points"
            title = f':trophy: {interaction.guild.name}\'s Care Points Leaderboard :trophy:'
            message = f'These points are earned through caring for your pony!\n\n'
        case 1:
            board = "server"
            nice_type = "Server Points"
            title = f':trophy: {interaction.guild.name}\'s Server Points Leaderboard :trophy:'
            message = f'These points are given out by your server\'s moderation team!\n\n'
        case _:
            await interaction.response.send_message(f'Please select a leaderboard type - 0 for Care Points, 1 for Server Points', ephemeral = True)
    server_data = await Client.get_server_data(server_id)
    channel = interaction.guild.get_channel(server_data[5])
    if not(interaction.channel_id == server_data[5]):
        await interaction.response.send_message(f'This needs to be sent in my specific channel please - {channel.mention} :horse::heart:', ephemeral= True)
    else:
        if not(board == ""):
            leaders = await Client.get_leaderboard(server_id, board)
            
            if leaders:
                placement = 1
                for L in leaders:
                    message += f'{placement}. {L[0]} and {L[1]} - {L[2]} pts\n' 
                    placement += 1
                

                embed = discord.Embed(title=title, description=message, color=BOT_COLOR)
                embed.set_footer(text=BOT_CREDITS)

                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f'The {nice_type} Leaderboard for has no members with points for this server. :cry:', ephemeral = True)


#####################################################################################################
################################# Stablecare core specific commands #################################
#####################################################################################################

#0-Personal(she) 1-Objective(her) 2-Possessive(hers) 3-Name(Mare) 
PRONOUNS_LOW = np.array([["she", "her", "her", "mare"], ["he", "him", "his", "stallion"], ["he", "him", "his", "gelding"]])
PRONOUNS_CAP = np.array([["She", "Her", "Her", "Mare"], ["He", "Him", "His", "Stallion"], ["He", "Him", "His", "Gelding"]])

#######################################################################################
################################# REGISTER NEW HORSES #################################
##SET UP A HORSE FOR YOURSELF
@client.tree.command(name="createpony", description="Set up your pony! Gender: 0-Mare 1-Stallion 2-Gelding", guild=GUILD_ID)
async def createAPony(interaction: discord.Interaction, pony_name: str, pony_gender : int):
    server_id = interaction.guild.id
    server_data = await Client.get_server_data(server_id)
    
    if server_data:
        log_channel = client.get_channel(server_data[4])
        channel = interaction.guild.get_channel(server_data[5])
        if not(interaction.channel_id == server_data[5]):
            await interaction.response.send_message(f'This needs to be sent in my specific channel please - {channel.mention} :horse::heart:', ephemeral= True)
        else:
            if pony_gender > 2 or pony_gender < 0:
                await interaction.response.send_message(f'Please try again and properly select a gender for your pony (0-2)', ephemeral = True)
            else:
                coat = random.randrange(1, 7)
                user_id = interaction.user.id
                user_name = interaction.user.display_name
                conn = connect_db() #connect to the database
                cursor = conn.cursor() #start work on the database. cursor will be the action to move through the database
                
                # Check if the user already exists in the database - cursor.execute will run a sql fn in the database
                cursor.execute(f"SELECT * FROM horse_information WHERE user_id = {user_id} AND server_id = {server_id}")
                user = cursor.fetchone() #fetchone() gets the first row of the results

                cursor.execute(f"SELECT * FROM preset_images WHERE coat_id = {coat}")
                coat_values = cursor.fetchone()

                if user: #if something was pulled above...
                    await interaction.response.send_message(f'Sorry {interaction.user.display_name}, you already have a horse!', ephemeral = True)
                    await log_channel.send(f'{interaction.user.display_name} attempted to rergister a second horse with the createapony command')
                else:
                    # Insert user data into the database
                    #await interaction.response.send_message("The SQL server does not have a horse registered to you.")
                    try:
                        QUERY = (
                            f'INSERT INTO horse_information (user_id, server_id, user_name, horse_name, gender, health, hunger, thirst, clean, money, bot_pts, server_pts, harpg_pts, coat, custom_thumb, stand_ref_image, happy_ref_img, sad_ref_img, feed_img, water_img, brush_img, treat_img, serial) '
                        + f'VALUES ({user_id}, {server_id}, \"{user_name}\", \"{pony_name}\", {pony_gender}, 7, 7, 7, 7, 30, 10, 0, 0, {coat}, 0, \"\", \"\", \"\", \"\", \"\", \"\", \"\", DEFAULT)' 
                        )
                        cursor.execute(QUERY)
                        conn.commit() #commits the information above to the database to save the addition of information
                        print(f'A new {coat_values[1]} horse named, {pony_name}, has been registered to {user_name}.')
                        await log_channel.send(f'{interaction.user.display_name} has registered a new {coat_values[1]} horse named, {pony_name}.')
                        
                        message = (f'Congrats! {pony_name} has come home to you! Please take good care of {PRONOUNS_LOW[pony_gender,1]}. :horse:')
                    
                        embed = discord.Embed(title="A new horse has arrived!", description=message, color= BOT_COLOR)
                        embed.set_image(url=coat_values[3])
                        
                        await interaction.response.send_message(embed=embed)

                    except mysql.connector.Error as e:
                        print(f'Error occurred while attempting to add a horse for {user_name} in {server_id}: {e}')
                        await log_channel.send(f'{interaction.user.display_name} has encountered an error while attempting to register a horse.')
                        await interaction.response.send_message(f'An error has occured while attempting to add your horse to our stable. Please contact an adminstrator for assistance.', ephemeral = True)

                conn.close() #safely exit the database connection

    else:
        await interaction.response.send_message(f'Your server is not set up to accept horses. Please have a server moderator set up the bot. Thank you!', ephemeral = True)

##SET UP A HORSE - ADMIN FOR ANOTHER USER
@client.tree.command(name="createponyadmin", description="Admin - Pony Set Up | Unique Discord User ID needed | Gender: 0-M 1-S 2-G", guild=GUILD_ID)
async def createAPonyADMIN(interaction: discord.Interaction, updating_user: str, pony_name: str, pony_gender : int):
    server_id = interaction.guild.id
    server_data = await Client.get_server_data(server_id)
    user_roles = interaction.user.roles

    user_id = int(updating_user.replace("<@", "").replace(">", ""))
    user_name = await client.fetch_user(user_id)
    admin_found = False

    if server_data:
        log_channel = client.get_channel(server_data[4])
        for role in user_roles:
            if role.id == server_data[3]:
                admin_found = True
                print(f'{interaction.user.display_name} ran the admin create a pony command.')
                if pony_gender > 2 or pony_gender < 0:
                    await interaction.response.send_message(f'Please try again and properly select a gender for their pony (0-2)')
                else:
                    coat = random.randrange(1, 7)

                    conn = connect_db() 
                    cursor = conn.cursor() 
                    
                    cursor.execute(f"SELECT * FROM horse_information WHERE user_id = {user_id} AND server_id = {server_id}")
                    user = cursor.fetchone() 

                    if user: 
                        await interaction.response.send_message(f'{user_name} already has a horse!', ephemeral= True)
                        await log_channel.send(f'{interaction.user.display_name} attempted to use the admin create a pony command - unsucessful - {user_name} already had a horse')
                    else:
                        try:
                            QUERY = (
                                f'INSERT INTO horse_information (user_id, server_id, user_name, horse_name, gender, health, hunger, thirst, clean, money, bot_pts, server_pts, harpg_pts, coat, custom_thumb) '
                              + f'VALUES ({user_id}, {server_id}, \"{user_name}\", \"{pony_name}\", {pony_gender}, 7, 7, 7, 7, 30, 10, 0, 0, {coat}, 0)' 
                            )
                            cursor.execute(QUERY)
                            conn.commit() 
                            await interaction.response.send_message(f'{pony_name} has been registered to {user_name}', ephemeral= True)
                            await log_channel.send(f'{interaction.user.display_name} ran the admin create a pony command to register a horse to {user_name}')
                        except mysql.connector.Error as e:
                            print(f'Error occurred while attempting to add a horse for {user_name}: {e}')
                            await log_channel.send(f'{interaction.user.display_name} attempted to use the admin create a pony command - unsuccessful - an error occurred while trying to register a horse for {user_name}')
                            await interaction.response.send_message(f'An error has occured while attempting to register a horse for {user_name}', ephemeral= True)

                    conn.close() 
        
        if not admin_found:
            await log_channel.send(f'{interaction.user.display_name} attempted to use the admin create a pony command')
            await interaction.response.send_message(f'Sorry, {interaction.user.display_name}, only Stablecare Barn Managers can run this command.', ephemeral=True)
    
    else:
        await interaction.response.send_message(f'Your server is not set up to accept horses. Please have a moderator set up this bot. Thank you.', ephemeral = True)

###############################################################################################
################################# CHECK ON YOUR HORSE'S STATS ################################# 
@client.tree.command(name="checkonpony", description="See how your horse is doing!", guild=GUILD_ID)
async def checkPony(interaction: discord.Interaction):
    server_id = interaction.guild.id
    user_id = interaction.user.id
    horse_data = await Client.gather_all_horse_data(user_id, server_id)

    if horse_data:
        server_data = await Client.get_server_data(server_id)
        channel = interaction.guild.get_channel(server_data[5])
        if not(interaction.channel_id == server_data[5]):
            await interaction.response.send_message(f'This needs to be sent in my specific channel please - {channel.mention} :horse::heart:', ephemeral= True)
        else:
            coat_values = await Client.gather_coat_values({horse_data[13]})
            stats_t = f'{horse_data[3]}\'s Care Stats'
            stats_v = await Client.stat_string(horse_data)

            points_t = f'{horse_data[3]}\'s Points'
            points_v = (
                #f'**Money: ** ${horse_data[10]}' + f'\n' +
                f'**Care Points: ** {horse_data[10]}'
            )
            if horse_data[11] > 0:
                points_v += f'\n**Server Points: ** {horse_data[11]}'
            if horse_data[12] > 0:
                points_v += f'\n**HARPG Points: ** {horse_data[12]}'

            skills_t = f'{horse_data[3]}\'s Discipline and Skills'

            dis_name = ""
            match horse_data[30]:
                case 0:
                    dis_name = "Dressage"
                case 1:
                    dis_name = "Show Jumping"
                case 2:
                    dis_name = "Barrel Racing"
                case 3:
                    dis_name = "Western Pleasure"

            has_shown = ""
            match horse_data[32]:
                case 0:
                    has_shown = f'{horse_data[3]} has *not* been entered in a show today.'
                case 1:
                    has_shown = f'{horse_data[3]} has been entered in today\'s show.'

            skills_v = (
                f'**Discipline: ** {dis_name} \n'+
                f'**Discipline Score: ** {horse_data[31]}\n\n'
                f'**Balance: ** {horse_data[26]}\n'+
                f'**Agility: ** {horse_data[27]}\n'+
                f'**Power: ** {horse_data[28]}\n'+
                f'**Flexibility: ** {horse_data[29]}\n\n' +
                f'{horse_data[3]} can do {3-horse_data[33]} training sessions right now.\n' +
                f'{has_shown}'
            )

            pony_name = f"**Name:** {horse_data[3]}"
            pony_gender = f"**Gender:** {PRONOUNS_CAP[horse_data[4],3]}"
            message = pony_name + f'\n' + pony_gender
            footer = f"{horse_data[3]} is happy you stopped by!"
            image = ""

            #print(f'{horse_data[0]}')
            if horse_data[14] == 1:
                if horse_data[8] == 10 and horse_data[7] == 10 and horse_data[6] == 10 and horse_data[5] == 10:
                    #print(f'{horse_data[3]} is happy.')
                    if horse_data[16] == "":
                        image = horse_data[15]
                    else:
                        image = horse_data[16]
                elif horse_data[8] > 5 and horse_data[7] > 4 and horse_data[6] > 5:
                    #print(f'{horse_data[3]} is content.')
                    image = horse_data[15]
                else:
                    #print(f'{horse_data[3]} is sad.')
                    if horse_data[17] == "":
                        image = horse_data[15]
                    else:
                        image = horse_data[17]
            else:
                if horse_data[8] == 10 and horse_data[7] == 10 and horse_data[6] == 10 and horse_data[5] == 10:
                    #print(f'{horse_data[3]} is happy.')
                    image = coat_values[3]
                elif horse_data[8] > 5 and horse_data[7] > 4 and horse_data[6] > 5:
                    #print(f'{horse_data[3]} is content.')
                    image = coat_values[2]
                else:
                    #print(f'{horse_data[3]} is sad.')
                    image = coat_values[4]
                    

            embed = discord.Embed(title="Horse Information", description=message, color= BOT_COLOR)
            if not(image == ""):
                embed.set_image(url=image) 
            embed.set_footer(text=footer)
            embed.add_field(name=points_t, value=points_v, inline= False)
            embed.add_field(name=skills_t, value=skills_v, inline= False)
            embed.add_field(name=stats_t, value=stats_v, inline= False)
            
            await interaction.response.send_message(embed=embed)         

    else:
        await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)


####################################################################################
################################# HORSE CARE MENUS #################################
####################################################################################
################################# Pets #################################
@client.tree.command(name="petpony", description="Pet your pony", guild=GUILD_ID)
async def pettingPony(interaction: discord.Interaction):
     user_id = interaction.user.id
     server_id = interaction.guild.id
     horse_data = await Client.gather_all_horse_data(user_id, server_id)
     server_data = await Client.get_server_data(server_id)
     channel = interaction.guild.get_channel(server_data[5])
     if not(interaction.channel_id == server_data[5]):
         await interaction.response.send_message(f'This needs to be sent in my specific channel please - {channel.mention} :horse::heart:', ephemeral= True)
     else:
         if horse_data:
             message = (f'{horse_data[3]} enjoys being petted. {PRONOUNS_CAP[horse_data[4],0]} loves the attention')
             title = f'Petting {horse_data[3]}'
             embed = discord.Embed(title=title, description=message, color= BOT_COLOR)
 
             if horse_data[14] == 0:
                coat_values = await Client.gather_coat_values(horse_data[13])
                embed.set_image(url = coat_values[9])
             if horse_data[14] == 1 and not(horse_data[22] == ""):
                 embed.set_image(url = horse_data[22])

             await interaction.response.send_message(embed=embed)
         else:
             await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)


################################# Food #################################
class FoodDropdown(discord.ui.Select):
    def __init__(self):

        # Set the options that will be presented inside the dropdown
        options = [
            discord.SelectOption(label='1 lb of Grain', emoji='🧺'),
            discord.SelectOption(label='2 lbs of Orchard hay', emoji='🌿'),
            discord.SelectOption(label='3 lbs of Timothy', emoji='🌾'),
            discord.SelectOption(label='4 lbs of Clover hay', emoji='☘️'),
            discord.SelectOption(label='5 lbs of Alfalfa', emoji='🥬'),
        ]

        # The placeholder is what will be shown when no option is chosen
        # The min and max values indicate we can only pick one of the three options
        # The options parameter defines the dropdown options. We defined this above
        super().__init__(placeholder='Feed your pony...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # the user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.

        user_id = interaction.user.id
        server_id = interaction.guild.id
        horse_data = await Client.gather_all_horse_data(user_id, server_id)
        selection_str = self.values[0]
        channel = interaction.channel.id 
        

        if horse_data:
            await interaction.response.send_message(f'You head to the feed room to collect {horse_data[3]}\'s meal.', ephemeral=True)
            await Client.feed_pony(user_id, server_id, horse_data, selection_str, channel)
            
        else:
            await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)
 
class FoodView(discord.ui.View):
    def __init__(self):
        super().__init__()

        # Adds the dropdown to our view object.
        self.add_item(FoodDropdown())
    
### display buttons
@client.tree.command(name="feed", description="Feed your pony!", guild=GUILD_ID)
async def food(interaction: discord.Interaction):
    """Sends a message with our dropdown containing colours"""

    # Create the view containing our dropdown
    view = FoodView()

    user_id = interaction.user.id
    server_id = interaction.guild.id
    horse_data = await Client.gather_all_horse_data(user_id, server_id)
        
    if horse_data:
        #await Client.update_horse_data(user_id, server_id, "hunger", 10)
        #if horse_data[6] < 10:
        message = ""
        if horse_data[6] == 10:
            message = (f'Are you sure you want to feed {horse_data[3]}? {PRONOUNS_CAP[horse_data[4],0]} doesn\' need any more food right now...')
        else:
            message = (f'Time to feed {horse_data[3]}! {PRONOUNS_CAP[horse_data[4],0]} needs {10-horse_data[6]} pounds of food.')
        # Sending a message containing our view
        server_data = await Client.get_server_data(server_id)
        channel = interaction.guild.get_channel(server_data[5])
        if not(interaction.channel_id == server_data[5]):
            await interaction.response.send_message(f'This needs to be sent in my specific channel please - {channel.mention} :horse::heart:', ephemeral= True)
        else:
            await interaction.response.send_message(message, view=view, delete_after=30)
    else:
        await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)


################################# Water #################################
class WaterDropdown(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label='1 gallon of water', emoji='🔹'),
            discord.SelectOption(label='2 gallons of water', emoji='🔷'),
            discord.SelectOption(label='3 gallons of water', emoji='💙'),
            discord.SelectOption(label='4 gallons of water', emoji='🔵'),
            discord.SelectOption(label='5 gallons of water', emoji='🟦'),
        ]

        super().__init__(placeholder='How much water do you add...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        server_id = interaction.guild.id
        horse_data = await Client.gather_all_horse_data(user_id, server_id)
        selection_str = self.values[0]
        channel = interaction.channel.id 
        

        if horse_data:
            await interaction.response.send_message(f'You fetch the hose to start adding water to {horse_data[3]}\'s water bucket.', ephemeral=True)
            await Client.water_pony(user_id, server_id, horse_data, selection_str, channel)
            
        else:
            await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)
        

class WaterView(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(WaterDropdown())
    

@client.tree.command(name="water", description="Fill your pony's water bucket", guild=GUILD_ID)
async def water(interaction: discord.Interaction):
    view = WaterView()

    user_id = interaction.user.id
    server_id = interaction.guild.id
    horse_data = await Client.gather_all_horse_data(user_id, server_id)
        
    if horse_data:
        message = ""
        if horse_data[7] == 10:
            message = (f'Are you sure you want to add water to {horse_data[3]}\'s bucket? {PRONOUNS_CAP[horse_data[4],2]} water bucket is full right now.')
        else:
            message = (f'Time to add water to {horse_data[3]}\'s bucket! {PRONOUNS_CAP[horse_data[4],0]} needs {10-horse_data[7]} gallons of water.')
        server_data = await Client.get_server_data(server_id)
        channel = interaction.guild.get_channel(server_data[5])
        if not(interaction.channel_id == server_data[5]):
            await interaction.response.send_message(f'This needs to be sent in my specific channel please - {channel.mention} :horse::heart:', ephemeral= True)
        else:
            await interaction.response.send_message(message, view=view, delete_after=30)
    else:
        await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)

################################# Vet #################################
class VetDropdown(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label='1 pts - Wellness Check', emoji='🩹'),
            discord.SelectOption(label='2 pts - Vaccines', emoji='💉'),
            discord.SelectOption(label='3 pts - Deworming', emoji='💊'),
            discord.SelectOption(label='4 pts - Body Work', emoji='🤲'),
            discord.SelectOption(label='5 pts - Dental Float', emoji='🦷'),
        ]

        super().__init__(placeholder='What service is the vet performing today...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        server_id = interaction.guild.id
        horse_data = await Client.gather_all_horse_data(user_id, server_id)
        selection_str = self.values[0]
        channel = interaction.channel.id 
        

        if horse_data:
            await interaction.response.send_message(f'You called the vet out to check out {horse_data[3]}.', ephemeral=True)
            await Client.vet_pony(user_id, server_id, horse_data, selection_str, channel)
            
        else:
            await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)
        

class VetView(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(VetDropdown())
    

@client.tree.command(name="vetcare", description="Call the vet to improve your pony's health!", guild=GUILD_ID)
async def vet(interaction: discord.Interaction):
    view = VetView()

    user_id = interaction.user.id
    server_id = interaction.guild.id
    horse_data = await Client.gather_all_horse_data(user_id, server_id)
        
    if horse_data:
        message = ""
        if horse_data[5] == 10:
            message = (f'Are you sure you want call out the vet? {horse_data[3]} is at full health.')
        else:
            message = (f'Time to call {horse_data[3]}\'s vet! {PRONOUNS_CAP[horse_data[4],0]} needs to regain {10-horse_data[5]} health points.')
        server_data = await Client.get_server_data(server_id)
        channel = interaction.guild.get_channel(server_data[5])
        if not(interaction.channel_id == server_data[5]):
            await interaction.response.send_message(f'This needs to be sent in my specific channel please - {channel.mention} :horse::heart:', ephemeral= True)
        else:
            await interaction.response.send_message(message, view=view, delete_after=30)
    else:
        await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)

################################# Grooming #################################
class GroomingDropdown(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label='1 pts - Light Brushing', emoji='🧽'),
            discord.SelectOption(label='2 pts - Thorough Groom', emoji='🧼'),
            discord.SelectOption(label='3 pts - Mane and Tail Braiding', emoji='🎀'),
            discord.SelectOption(label='4 pts - Full Body Bath', emoji='🛁'),
        ]

        super().__init__(placeholder='What grooming activity are you doing today...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        server_id = interaction.guild.id
        horse_data = await Client.gather_all_horse_data(user_id, server_id)
        selection_str = self.values[0]
        channel = interaction.channel.id 
        

        if horse_data:
            await interaction.response.send_message(f'You go to the tack room to fetch {horse_data[3]}\'s brushes.', ephemeral=True)
            await Client.groom_pony(user_id, server_id, horse_data, selection_str, channel)
            
        else:
            await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)
        

class GroomingView(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(GroomingDropdown())
    

@client.tree.command(name="groom", description="Clean your pony!", guild=GUILD_ID)
async def groom(interaction: discord.Interaction):
    view = GroomingView()

    user_id = interaction.user.id
    server_id = interaction.guild.id
    horse_data = await Client.gather_all_horse_data(user_id, server_id)
        
    if horse_data:
        message = ""
        if horse_data[8] == 10:
            message = (f'Are you sure you want to groom {horse_data[3]}? {PRONOUNS_CAP[horse_data[4],0]} is perfectly.')
        else:
            message = (f'Time to groom {horse_data[3]}! {PRONOUNS_CAP[horse_data[4],0]} needs to regain {10-horse_data[8]} cleanliness points.')
        
        server_data = await Client.get_server_data(server_id)
        channel = interaction.guild.get_channel(server_data[5])
        if not(interaction.channel_id == server_data[5]):
            await interaction.response.send_message(f'This needs to be sent in my specific channel please - {channel.mention} :horse::heart:', ephemeral= True)
        else:
            await interaction.response.send_message(message, view=view, delete_after=30)
    else:
        await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)

################################# Grooming #################################
class TreatsDropdown(discord.ui.Select):
    def __init__(self):

        options = [
            discord.SelectOption(label='Apple', emoji='🍎'),
            discord.SelectOption(label='Peppermint', emoji='🍬'),
            discord.SelectOption(label='Sugarcube', emoji='🧊'),
            discord.SelectOption(label='Carrot', emoji='🥕'),
            discord.SelectOption(label='Cookie', emoji='🍪'),
        ]

        super().__init__(placeholder='What treat are you feeding you pony...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        server_id = interaction.guild.id
        horse_data = await Client.gather_all_horse_data(user_id, server_id)
        selection_str = self.values[0]
        channel = interaction.channel.id 
        

        if horse_data:
            await interaction.response.send_message(f'You have fetched the treats for {horse_data[3]}.', ephemeral=True)
            await Client.treat_pony(user_id, server_id, horse_data, selection_str, channel)
            
        else:
            await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)
        

class TreatsView(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.add_item(TreatsDropdown())
    

@client.tree.command(name="treats", description="Feed your pony a treat!", guild=GUILD_ID)
async def treat(interaction: discord.Interaction):
    view = TreatsView()

    user_id = interaction.user.id
    server_id = interaction.guild.id
    horse_data = await Client.gather_all_horse_data(user_id, server_id)
        
    if horse_data:
        message = (f'Time to give {horse_data[3]} a treat!')
        server_data = await Client.get_server_data(server_id)
        channel = interaction.guild.get_channel(server_data[5])
        if not(interaction.channel_id == server_data[5]):
            await interaction.response.send_message(f'This needs to be sent in my specific channel please - {channel.mention} :horse::heart:', ephemeral= True)
        else:
            await interaction.response.send_message(message, view=view, delete_after=30)
    else:
        await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)


####################################################################################
################################# TRAINING COMMANDS #################################
####################################################################################
################################# Pets #################################
### Disciplines:
##### 0 - Dressage -- balance_sk / flex_sk / agility_sk
##### 1 - Show Jumping -- balance_sk / power_sk / agility_sk
##### 2 - Barrel Racing -- power_sk / flex_sk / agility_sk
##### 3 - Western Pleasure -- balance_sk / flex_sk / power_sk
@client.tree.command(name="trainpony", description="Train your pony in Flexibility, Balance, Power, or Agility.", guild=GUILD_ID)
async def trainPony(interaction: discord.Interaction, skill_to_train: str):
    user_id = interaction.user.id
    server_id = interaction.guild.id
    horse_data = await Client.gather_all_horse_data(user_id, server_id)
    
    skill_to_train = skill_to_train.lower()
    column = ""
    skill_name = ""
    array_value = 0
    match skill_to_train:
        case "balance":
            column = "balance_sk"
            skill_name = "Balance"
            array_value = 26
        case "agility":
            column = "agility_sk"
            skill_name = "Agility"
            array_value = 27
        case "speed":
            column = "agility_sk"
            skill_name = "Agility"
            array_value = 27
        case "jump":
            column = "power_sk"
            skill_name = "Power"
            array_value = 28
        case "jumping":
            column = "power_sk"
            skill_name = "Power"
            array_value = 28
        case "power":
            column = "power_sk"
            skill_name = "Power"
            array_value = 28
        case "flex":
            column = "flex_sk"
            skill_name = "Flexibility"
            array_value = 29
        case "flexibility":
            column = "flex_sk"
            skill_name = "Flexibility"
            array_value = 29    

    if horse_data:
        server_data = await Client.get_server_data(server_id)
        channel = interaction.guild.get_channel(server_data[5])
        if not(interaction.channel_id == server_data[5]):
            await interaction.response.send_message(f'This needs to be sent in my specific channel please - {channel.mention} :horse::heart:', ephemeral= True)
        else:
            if horse_data[33] == 3:
                await interaction.response.send_message(f'{horse_data[3]}, has already had 3 training sessions. {PRONOUNS_CAP[horse_data[4], 0]} needs a rest. {PRONOUNS_CAP[horse_data[4], 0]} can do more training sessions after the barn update.', ephemeral= True)

            else:
                if array_value == 0:
                    await interaction.response.send_message(f'The skills you can train are Balance, Agility (Speed), Power (Jumping), and Flexibility. Please select one of these options to train {horse_data[3]} in.', ephemeral= True)

                else:
                    await interaction.response.send_message(f'Heading out for a ride...', ephemeral= True)

                    skill_level = horse_data[array_value]
                    level = 0
                    lvl_up_msg = ""
                    if skill_level >= 0 or skill_level < 11:
                        level = 1
                        lvl_up_msg = f'{PRONOUNS_CAP[horse_data[4], 0]} needs {10-skill_level} more points to level up.'
                    elif skill_level >= 10 or skill_level < 21:
                        level = 2
                        lvl_up_msg = f'{PRONOUNS_CAP[horse_data[4], 0]} needs {20-skill_level} more points to level up.'
                    elif skill_level >= 20 or skill_level < 30:
                        level = 3
                        lvl_up_msg = f'{PRONOUNS_CAP[horse_data[4], 0]} needs {30-skill_level} more points to level up.'
                    elif skill_level == 30:
                        level = 3
                        lvl_up_msg = f'{PRONOUNS_CAP[horse_data[4], 0]} is maxxed out in this skill... but {horse_data[3]} is welcome to continue to practice {PRONOUNS_LOW[horse_data[4], 2]} {skill_name.lower()} skill!'
                    
                    question = await Client.get_question(level)
                    
                    title = f'Time to train {horse_data[3]} in the {skill_name} skill!'
                    content = (
                        f'\n\n{horse_data[3]} is level {level} in {skill_name}.' +
                        f'\n{lvl_up_msg}' +
                        f'\n\n**Answer the below question to train {horse_data[3]}.**' +
                        f'\n{question[1]}'
                    )
                    embed = discord.Embed(title=title, description=content, color= BOT_COLOR)
                    
                    embed.set_footer(text="All answers are whole numbers (positive or negative). Only type a number.")

                    await channel.send(embed=embed)

                    def check(m):
                        return m.author == interaction.user and m.channel == channel

                    msg = await client.wait_for('message', check=check)
                    
                    if msg.content == str(question[2]):
                        new_skl_lvl = skill_level + 1
                        if new_skl_lvl > 30:
                            new_skl_lvl = 30
                        await Client.update_horse_data(user_id, server_id, column, new_skl_lvl)
                        await Client.discipline_level(user_id, server_id, horse_data, horse_data[30])

                        title = f'{horse_data[3]} improved {PRONOUNS_LOW[horse_data[4], 2]} {skill_name} skill!'
                        content = f'Congrats! You and {horse_data[3]} had a great ride and improved in {skill_name}.'
                        
                        if new_skl_lvl == 10 or new_skl_lvl == 20:
                            content += f'\n\n{horse_data[3]} has leveled up in {skill_name}!'
                        elif new_skl_lvl == 30:
                            content += f'\n\n{horse_data[3]} has maxxed out {PRONOUNS_LOW[horse_data[4], 2]} {skill_name} skill! {PRONOUNS_CAP[horse_data[4], 2]} is happy to continue practicing {PRONOUNS_LOW[horse_data[4], 2]} {skill_name.lower()} but can\'t gain any more skill points.'
                        else:
                            next_lvl = (level * 10) - new_skl_lvl
                            content += f'\n\n{horse_data[3]} needs {next_lvl} more skill points to level up.'

                    else:
                        title = f'{horse_data[3]} had a bad ride.'
                        content = (
                            f'Unfortunately, {horse_data[3]} wasn\'t able to learn enough in this ride to gain a skill point in {skill_name}. Hopefully, the next ride will be better!'
                        )
                        next_lvl = (level * 10) - skill_level
                        content += f'\n\n{horse_data[3]} needs {next_lvl} more skill points to level up.'
                        content += f'\n\nYou attempted question {question[0]} of Level {level}.'
                        content += f'\nThe correct answer was: {question[2]}'
                        if level > 1:
                            help_text = str(question[3])
                            content += f'\n{help_text}'
                            content += f'\nYou got it next time for sure!'
                        else:
                            content += f'\nRemeber your math facts, you got it next time!'

                    trainings = horse_data[33] + 1
                    await Client.update_horse_data(user_id, server_id, "daily_trainings", trainings)
                    
                    embed = discord.Embed(title=title, description=content, color= BOT_COLOR)
                    
                    if horse_data[14] == 0:
                        coat_values = await Client.gather_coat_values(horse_data[13])
                        embed.set_image(url = coat_values[10])
                    if horse_data[14] == 1 and not(horse_data[23] == ""):
                        embed.set_image(url = horse_data[23])
                    
                    footer = ""
                    if horse_data[33] == 2:
                        footer = f'{horse_data[3]} can not do more training sessions right now. {PRONOUNS_CAP[horse_data[4], 0]} needs a rest. {PRONOUNS_CAP[horse_data[4], 0]} can do more training sessions after the barn update.'
                    else:
                        footer = f'{horse_data[3]} can do {2-horse_data[33]} more training sessions right now.'
                    embed.set_footer(text=footer)

                    await channel.send(embed=embed)

    else:
        await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)


@client.tree.command(name="setdiscipline", description="Select your pony's job - Dressage, Jumping, Rodeo, or Pleasure.", guild=GUILD_ID)
async def setDiscipline(interaction: discord.Interaction, discipline: str):
    user_id = interaction.user.id
    server_id = interaction.guild.id
    horse_data = await Client.gather_all_horse_data(user_id, server_id)
    choice = -1
    discipline = discipline.lower()
    dis_name = ""
    match discipline:
        case "dressage":
            choice = 0
            dis_name = "Dressage"
        case "dance":
            choice = 0
            dis_name = "Dressage"
        case "jumping":
            choice = 1
            dis_name = "Show Jumping"
        case "cross country":
            choice = 1
            dis_name = "Show Jumping"
        case "show jumping":
            choice = 1
            dis_name = "Show Jumping"
        case "hunter":
            choice = 1
            dis_name = "Show Jumping"
        case "hunter jumper":
            choice = 1
            dis_name = "Show Jumping"
        case "rodeo":
            choice = 2
            dis_name = "Barrel Racing"
        case "pole bending":
            choice = 2
            dis_name = "Barrel Racing"
        case "barrel racing":
            choice = 2
            dis_name = "Barrel Racing"
        case "racing":
            choice = 2
            dis_name = "Barrel Racing"
        case "wp":
            choice = 3
            dis_name = "Western Pleasure"
        case "western":
            choice = 3
            dis_name = "Western Pleasure"
        case "pleasure":
            choice = 3
            dis_name = "Western Pleasure"
        case "western pleasure":
            choice = 3
            dis_name = "Western Pleasure"
    
    if horse_data:
        if choice == -1:
            await interaction.response.send_message("Please select one of our disciplines - Dressage, Show Jumping, Barrel Racing (Rodeo), or Western Pleasure.", ephemeral=True)
        else:
            await Client.update_horse_data(user_id, server_id, "discipline", choice)
            await Client.discipline_level(user_id, server_id, horse_data, choice)

            horse_data = await Client.gather_all_horse_data(user_id, server_id)
            
            content = (
                f'**{horse_data[3]} has been registered as a {dis_name} pony!**'+
                f'\n{PRONOUNS_CAP[horse_data[4],0]} has a base {dis_name} stat level of {horse_data[31]}.'
            )               
            
            await interaction.response.send_message(content, ephemeral=True)
    else:
        await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)
        

@client.tree.command(name="entershow", description="Enter into today's horse show!", guild=GUILD_ID)
async def enterShow(interaction: discord.Interaction):
    user_id = interaction.user.id
    server_id = interaction.guild.id
    horse_data = await Client.gather_all_horse_data(user_id, server_id)
    server_data = await Client.get_server_data(server_id)

    clase_name = ""
    match server_data[7]:
        case 0:
            clase_name = "Dressage"
        case 1:
            clase_name = "Show Jumping"
        case 2:
            clase_name = "Barrel Racing"
        case 3:
            clase_name = "Western Pleasure"

    choice_skill = random.randrange(1, 3)
    class_skill_value = -1
    match horse_data[30]:
        case 0:
            match choice_skill:
                case 1:
                    class_skill_value = horse_data[26]
                case 2:
                    class_skill_value = horse_data[29]
                case 3:
                    class_skill_value = horse_data[27]
        case 1:
            match choice_skill:
                case 1:
                    class_skill_value = horse_data[26]
                case 2:
                    class_skill_value = horse_data[28]
                case 3:
                    class_skill_value = horse_data[27]
        case 2:
            match choice_skill:
                case 1:
                    class_skill_value = horse_data[28]
                case 2:
                    class_skill_value = horse_data[29]
                case 3:
                    class_skill_value = horse_data[27]
        case 3:
            match choice_skill:
                case 1:
                    class_skill_value = horse_data[26]
                case 2:
                    class_skill_value = horse_data[29]
                case 3:
                    class_skill_value = horse_data[28] 


    if horse_data:
        channel = interaction.guild.get_channel(server_data[5])
        if not(interaction.channel_id == server_data[5]):
            await interaction.response.send_message(f'This needs to be sent in my specific channel please - {channel.mention} :horse::heart:', ephemeral= True)
        else:
            if horse_data[32] == 1:
                    await interaction.response.send_message(f'{horse_data[3]} is already entered in today\'s {clase_name} show!', ephemeral= True)
            else:
                if horse_data[33] == 3:
                    await interaction.response.send_message(f'{horse_data[3]}, has already had 3 training sessions. {PRONOUNS_CAP[horse_data[4], 0]} is too tired to show right now. {PRONOUNS_CAP[horse_data[4], 0]} can enter after the barn update.', ephemeral= True)

                else:
                    if not(horse_data[30] == server_data[7]):
                        message = (
                            f'Today\'s is a {clase_name} show, and {horse_data[3]} is not registered as a {clase_name} horse.' +
                            f'\nTo enter {horse_data[3]} in today\'s {clase_name} show, change {PRONOUNS_LOW[horse_data[4], 2]} discipline through the \'/setdiscipline\' command.'
                        )
                        await interaction.response.send_message(message, ephemeral= True)

                    else:
                        await interaction.response.send_message(f'Hauling out for a show...', ephemeral= True)
                        skip = False
                        correct = False

                        level = 0
                        if class_skill_value >= 0 or class_skill_value < 11:
                            level = 1
                        elif class_skill_value >= 10 or class_skill_value < 21:
                            level = 2
                        elif class_skill_value >= 20 or class_skill_value < 31:
                            level = 3
                        elif class_skill_value >= 30:
                            level = 3

                        question = await Client.get_question(level)
                        
                        title = f'Enter {horse_data[3]} into a {clase_name} Show!'
                        content = (
                            f'\n\n{horse_data[3]} has a starting {clase_name} stat of {horse_data[31]}.' +
                            f'\nAnswering the show question will earn you extra points to help your score!' +
                            f'\nHaving second thoughts? Type \'Exit\' to not enter {horse_data[3]} in today\'s show.'+
                            f'\n\n**Answer the below question to enter {horse_data[3]} in the show.**' +
                            f'\n{question[1]}'
                        )
                        embed = discord.Embed(title=title, description=content, color= BOT_COLOR)
                        
                        embed.set_footer(text="All answers are whole numbers (positive or negative). Only type a number.")

                        await channel.send(embed=embed, )

                        def check(m):
                            return m.author == interaction.user and m.channel == channel

                        msg = await client.wait_for('message', check=check)
                        
                        if msg.content == str(question[2]):
                            correct = True
                            title = f'{horse_data[3]} is excellently warmed up!'
                            content = f'You and {horse_data[3]} have a great warm up ride, giving {horse_data[3]} a temporary boost to {PRONOUNS_LOW[horse_data[4],2]} {clase_name} skills!'
                            

                        elif msg.content.lower() == "exit":
                            skip = True
                            await channel.send(f'You decide to scratch {horse_data[3]} from the class. You and {horse_data[3]} have a blast cheering on your friends!')

                        else:
                            title = f'{horse_data[3]} is ready to ride.'
                            content = f'You and {horse_data[3]} have an okay warm up ride... could have been better but its okay. You know that you and {horse_data[3]} are going to try your best and that is enough. :heart:'

                            content += f'\n\nYou attempted question {question[0]} of Level {level}.'
                            content += f'\nThe correct answer was: {question[2]}'
                            if level > 1:
                                help_text = str(question[3])
                                content += f'\n{help_text}'
                                content += f'\nYou got it next time for sure!'
                            else:
                                content += f'\nRemeber your math facts, you got it next time!'

                        
                        embed = discord.Embed(title=title, description=content, color= BOT_COLOR)
                        
                        if horse_data[14] == 0:
                            coat_values = await Client.gather_coat_values(horse_data[13])
                            embed.set_image(url = coat_values[11])
                        if horse_data[14] == 1 and not(horse_data[24] == ""):
                            embed.set_image(url = horse_data[24])
                        
                        footer = f'{horse_data[3]} has been entered into the {clase_name} show!'
                        embed.set_footer(text=footer)
                        
                        if not skip:
                            trainings = horse_data[33] + 1
                            await Client.update_horse_data(user_id, server_id, "daily_trainings", trainings)
                            await Client.update_horse_data(user_id, server_id, "is_showing", 1)
                            await Client.show_score(user_id, server_id, horse_data, correct)
                            await channel.send(embed=embed)

    else:
        await interaction.response.send_message(NO_HORSE_ERROR_MESSAGE, ephemeral=True)

################################# BOT RUN COMMANDS #################################
client.run('')