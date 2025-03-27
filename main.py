import numpy as np
import mysql.connector
import discord
from discord.ext import commands
from discord import app_commands

SERVER = 0 #add testing discord server id here

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

        try: #force syncing with the dev server to test commands
            guild=discord.Object(id=SERVER)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to guild {guild.id}')

        except Exception as e: #find errors with the syncing of commands
            print(f'Error syncing commands: {e}')

    
    async def on_message(self, message): #reading and responding to messages
        if message.author == self.user:
            return
        if message.content.startswith('hello'):
            await message.channel.send(f'Hello there {message.author} :horse: :heart:')

    async def on_reaction_add(self, reaction): #reading and responding to reactions
        await reaction.message.channel.send('You reacted... terminating bot')
        await close()

    ########################################################################################
    ################################# STABLECARE FUNCTIONS #################################
    ### gathering information for the horse based in provided user id
    async def gather_all_horse_data(user_id):
        conn = connect_db()
        cursor = conn.cursor()

        SELECTION_STR = (f-'SELECT * from horse_information WHERE user_id = {user_id}')
        
        cursor.execute(SELECTION_STR)
        horse_data = cursor.fetchone()
        
        conn.close()
        
        return horse_data
    
    ### update table information for a horse
    async def update_horse_data(user_id, data_column, updated_value)
        try:
            conn = connect_db()
            cursor = conn.cursor()

            QUERY_STR = (f-'UPDATE horse_information SET {data_column}  = ? WHERE user_id = ?')
            
            cursor.execute(QUERY_STR, (updated_value, user_id))
            conn.commit
            
            conn.close()
            return True

        except mysql.Error as e:
            print(f"An error has happened while attempting to update data: {e}")
            return False

    ### update all table values to reduce horse feed and water stats
    async def daily_horse_update(self)
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            #update hunger
            cursor.execute("UPDATE horse_information SET hunger = hunger - 3")
            conn.commit
            cursor.execute("UPDATE horse_information SET hunger = 0 WHERE hunger < 0")
            conn.commit

            #update thirst
            cursor.execute("UPDATE horse_information SET thirst = thirst - 5")
            conn.commit
            cursor.execute("UPDATE horse_information SET thirst = 0 WHERE thirst < 0")
            conn.commit

            #update cleanilness
            cursor.execute("UPDATE horse_information SET clean = clean - 3")
            conn.commit
            cursor.execute("UPDATE horse_information SET clean = 0 WHERE clean < 0")
            conn.commit

            #update health
            cursor.execute("UPDATE horse_information SET health = health - 2 WHERE hunger <= 5 AND thirst <= 5")
            conn.commit
            cursor.execute("UPDATE horse_information SET health = 0 WHERE health < 0")
            conn.commit

            conn.close()
            return True
            
        except mysql.Error as e:
            print(f'An error has happened while attempting to update all horses values: {e}')
            return False

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
@client.tree.command(name="hello", description="Says hello :)", guild=GUILD_ID)
async def sayHello(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hello there {interaction.user.display_name}!')

@client.tree.command(name="printer", description="I will say whatever you want :3", guild=GUILD_ID)
async def printer(interaction: discord.Interaction, printer: str): 
    #now printer is a variable that is accepted by the slash command with the accepted type of a string
    #the variable name is the value of the little black box in discord
    await interaction.response.send_message(printer)

#demo for how to build an embed
@client.tree.command(name="embed", description="Demo for embed messages", guild=GUILD_ID)
async def embedDemo(interaction: discord.Interaction): 
    embed = discord.Embed(title="I am a title", url="https://www.google.com", discripton="I am a description", color=discord.Color.teal)
    #url will turn the title to a link
    #color can be any value so long as you specify it (RGB/HEX/etc) - currently using the preset colors from discord.py

    embed.set_thumbnail(url="http://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/00cbf0f6-e2a4-4246-8615-24f03ef477c3/df8bk75-38c1d630-471c-425c-bd0e-9c84887e0641.png/v1/fill/w_1280,h_905,q_80,strp/first_touches_by_kyraltre3_df8bk75-fullview.jpg?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7ImhlaWdodCI6Ijw9OTA1IiwicGF0aCI6IlwvZlwvMDBjYmYwZjYtZTJhNC00MjQ2LTg2MTUtMjRmMDNlZjQ3N2MzXC9kZjhiazc1LTM4YzFkNjMwLTQ3MWMtNDI1Yy1iZDBlLTljODQ4ODdlMDY0MS5wbmciLCJ3aWR0aCI6Ijw9MTI4MCJ9XV0sImF1ZCI6WyJ1cm46c2VydmljZTppbWFnZS5vcGVyYXRpb25zIl19.1H8DDpq95SYgIVWZqdh8VZjXPDuKkolvlIkKuNY6yDM")
    
    #unlimted fields can be added (aparently, dont overdo it tho lol)
    embed.add_field(name="This is a field", value="This is text associated with field 1", inline=False) 
    #inline isn't required but is true by default, so the two fields below will be shown side by side while the one above is by itself.
    embed.add_field(name="This is a field (2)", value="This is text associated with field 2")
    embed.add_field(name="This is a field (3)", value="This is text associated with field 3")

    embed.set_footer(text="I am smol text at the bottom of the embed!")
    embed.set_author(name=interaction.user.name, url="https://www.google.com", icon_url="https://www.image.com")
    #the embed author can be set with this method and it currently shows as the person that sent the command. 
    #the author text can be made into a url and the icon image set in this method as seen above. 

    await interaction.response.send_message(embed=embed) #send the embed!

#############################################################################################################################################
################################# MANUALLY PUSH THE UPDATE TO ALL HORSE STATS AND RETURN YOUR HORSE'S STATS #################################
@client.tree.command(name="dailyupdate", description="Updates all horse values", guild=GUILD_ID)
async def runDailyUpdate(interaction: discord.Interaction):
    result = self.daily_horse_update()
    if result:
        user_id = interaction.user_id
        horse_data = self.gather_all_horse_data(user_id)

        if !horse_data:
            await interaction.response.send_message(f'The update has been run... but you don\'t have a horse to see their updated stats on.')
        else:
            await interaction.response.send_message(f'The update has been run. Your horse {horse_data[2]} has the following stats.')
            await interaction.response.send_message(f'Hunger: {horse_data[5]}')
            await interaction.response.send_message(f'Thirst: {horse_data[6]}')
            await interaction.response.send_message(f'Cleanliness: {horse_data[7]}')
            await interaction.response.send_message(f'Health: {horse_data[4]}')
    else:
        await interaction.response.send_message(f'An error occurred while trying to run the update.')

####################################################################################
################################# REMOVE USER DATA #################################
@client.tree.command(name="removedata", description="Removes all your data from this bot - type YES to remove your data", guild=GUILD_ID)
async def runDailyUpdate(interaction: discord.Interaction, confirmation_to_remove_data: str):
    user_id = interaction.user.id
    user_name = interaction.user.display_name

    if confirmation_to_remove_data == "YES":
        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            cursor.execute(f'DELETE FROM horse_information WHERE user_id = {user_id}')
            conn.commit

            conn.close()

            print(f'Successfully deleted {user_name}\'s data')
            await interaction.response.send_message(f'Your data has been successfully removed from this bot. Thank you for your time with us. :heart:')

        
        except mysql.Error as e:
            print(f'An error occurred while trying to remove {user_name}\'s data: {e}')
            await interaction.response.send_message(f'An error occurred while trying to delete your data. Please contact an adminstrator')

    else:
        await interaction.response.send_message(f'Confirmation not recieved, if you want to remove your data from this bot. Type \'YES\' in the confirmation field')

#####################################################################################################
################################# Stablecare core specific commands #################################
#####################################################################################################

#0-Personal(she) 1-Objective(her) 2-Possessive(hers) 3-Name(Mare) 
PRONOUNS = np.array([["she", "her", "hers", "Mare"], ["he", "him", "his", "Stallion"], ["he", "him", "his", "Gelding"], ["they", "them", "their", "Horse"]])

##SET UP A HORSE
@client.tree.command(name="createpony", description="Set up your pony! Gender: 0-Mare 1-Stallion 2-Gelding 3-Use 'They' pronouns", guild=GUILD_ID)
async def createAPony(interaction: discord.Interaction, pony_name: str, pony_gender : int):
    if pony_gender > 3 or pony_gender < 0:
        await interaction.response.send_message(f'Please try again and properly select a gender for your pony (0-2)')
    else:
        user_id = interaction.user.id
        user_name = interaaction.user.display_name
        conn = connect_db() #connect to the database
        cursor = conn.cursor() #start work on the database. cursor will be the action to move through the database
        
        # Check if the user already exists in the database - cursor.execute will run a sql fn in the database
        cursor.execute("SELECT * FROM horse_information WHERE user_id = %s", (user_id,))
        user = cursor.fetchone() #fetchone() gets the first row of the results

        if user: #if something was pulled above...
            await interaction.response.send_message(f'{interaction.user.id}, you already have a horse!')
        else:
            # Insert user data into the database
            cursor.execute("INSERT INTO horse_information (user_id, user_name, horse_name, gender, health, hunger, thirst, clean, money) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (user_id, user_name, pony_name, pony_gender, 10, 10, 10, 10, 30))
            conn.commit() #commits the information above to the database to save the addition of information
            await interaction.response.send_message(f'Congrats! {pony_name} has come home to you! Please take good care of {PRONOUNS[pony_gender,1]}. :horse:')

        conn.close() #safely exit the database connection

#######################################################################################
################################# HORSE CARE COMMANDS #################################
@client.tree.command(name="treats", description="Give your pony a treat. Type in whatever treat you want to feed your pony!", guild=GUILD_ID)
async def treatSnacking(interaction: discord.Interaction, treat_type: str):
    user_id = interaction.user_id
    horse_data = self.gather_all_horse_data(user_id)

    await interaction.response.send_message(f'{horse_data[2]} snacks on {treat_type}. {PRONOUNS[horse_data[3],0]} loved it!')

@client.tree.command(name="feed", description="Feed your pony. Type in whatever hay type and pounds you want to feed your pony", guild=GUILD_ID)
async def foodTime(interaction: discord.Interaction, feed_type: str, feed_amount: int):
    user_id = interaction.user_id
    horse_data = self.gather_all_horse_data(user_id)
    update = update_horse_data(user_id, hunger, 10)
    if update == false:
        await interaction.response.send_message(f'Sorry, {interaction.user.display_name}, we don\'t have a horse registered to you')
    else
    await interaction.response.send_message(f'You feed {horse_data[2]} {feed_amount}lbs of {feed_type}. {PRONOUNS[horse_data[3],0]} are full and satisfied.')

@client.tree.command(name="water", description="Fills your pony's water bucket", guild=GUILD_ID)
async def waterTime(interaction: discord.Interaction):
    user_id = interaction.user_id
    horse_data = self.gather_all_horse_data(user_id)
    update = update_horse_data(user_id, thirst, 10)
    if update == false:
        await interaction.response.send_message(f'Sorry, {interaction.user.display_name}, we don\'t have a horse registered to you')
    else:
        await interaction.response.send_message(f'{horse_data[2]}\'s water bucket is now full. {PRONOUNS[horse_data[3],0]} takes a nice long sip.')

@client.tree.command(name="vetcare", description="Heal your pony. Services Menu: 1-Vaccines 2-Dental 3-Check up", guild=GUILD_ID)
async def vetServices(interaction: discord.Interaction, vet_services: int):
    user_id = interaction.user_id
    horse_data = self.gather_all_horse_data(user_id)
    update = update_horse_data(user_id, health, 10)
    if update == false:
        await interaction.response.send_message(f'Sorry, {interaction.user.display_name}, we don\'t have a horse registered to you')
    else
        if vet_services == 1:
            await interaction.response.send_message(f'{horse_data[2]} stood for {PRONOUNS[horse_data[3],2]} shots. {PRONOUNS[horse_data[3],0]} were a very brave pony!')
        if vet_services == 2:
        if vet_services == 3:
            await interaction.response.send_message(f'The vet did a once over on {horse_data[2]}. They said {horse_data[2]} is the picture of health!')
        else:
            await interaction.response.send_message("The vet can't provide services if you don't select any. Please select a service from the list (1-3)")



################################# BOT RUN COMMANDS #################################
client.run('')