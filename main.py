import numpy as np
import discord
from discord.ext import commands
from discord import app_commands

#this is for standard functions
class Client(commands.Bot):
    async def on_ready(self): #on launch
        print(f'Successfully connected as {self.user}.')

        try: #force syncing with the dev server to test commands
            guild=[guild_ID values]
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)}" commands to guild {guild.id}')

        except Exception as e: #find errors witht he syncing
            print(f'Error syncing commands: {e}')

    
    async def on_message(self, message): #reading and responding to messages
        if message.author == self.user:
            return
        if message.content.startswith('hello'):
            await message.channel.send(f'Hello there {message.author} :horse: :heart:')

    async def on_reaction_add(self, reaction, user): #reading and responding to reactions
        await reaction.message.channel.send('You reacted')


intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents) #prefixes are outdated however still required in the call functions

GUILD_ID = discord.Object(id=[discord server id]) #add testing discord server id here
#commands are not globally used as it takes 1+hrs to actually get to all discord servers when globally triggered

# this is for slash commands, names of commands have to be lower case
# descriptions can have upper case
@client.tree.command(name-"hello", description="Says hello :)", guild=GUILD_ID)
async def sayHello(interaction: discord.interaction):
    await interaction.response.send_message("Hello there!")

@client.tree.command(name-"printer", description="I will say whatever you want :3", guild=GUILD_ID)
async def printer(interaction: discord.interaction, printer: str): 
    #now printer is a variable that is accepted by the slash command with the accepted type of a string
    #the variable name is the value of the little black box in discord
    await interaction.response.send_message(printer)


#Stablecare bot specific commands
PONY_NAME : str = "Pony"
PONY_PRONOUN : int = 2
PRONOUNS = np.array([[she, her, hers, hers], [he, him, his, his], [they, them, their, theirs]])

@client.tree.command(name-"create_pony", description="Set up your pony! Gender: 0-Mare 1-Gelding/Stallion 2-Use 'They' pronouns", guild=GUILD_ID)
async def createAPony(interaction: discord.interaction, pony_name: str, pony_gender : int):
    if pony_gender > 2 or pony_gender < 0:
        await interaction.response.send_message(f'Please try again and properly select a gender for your pony (0-2)')
    else:
        PONY_NAME = pony_name
        PONY_PRONOUN = pony_gender
        await interaction.response.send_message(f'Congrats! {PONY_NAME} has come home to you! Please take good care of {PRONOUNS[PONY_PRONOUN,1]}. :horse:')


@client.tree.command(name-"treats", description="Give your pony a treat. Type in whatever treat you want to feed your pony!", guild=GUILD_ID)
async def treatSnacking(interaction: discord.interaction, treat_type: str):
    await interaction.response.send_message(f'{PONY_NAME} snacks on {treat_type}. {PRONOUNS[PONY_PRONOUN,0]} loved it!')

@client.tree.command(name-"feed", description="Feed your pony. Type in whatever hay type and pounds you want to feed your pony", guild=GUILD_ID)
async def foodTime(interaction: discord.interaction, feed_type: str, feed_amount: int):
    await interaction.response.send_message(f'You feed {PONY_NAME} {feed_amount}lbs of {feed_type}. {PRONOUNS[PONY_PRONOUN,0]} are full and satisfied.')

@client.tree.command(name-"water", description="Fills your pony's water bucket", guild=GUILD_ID)
async def waterTime(interaction: discord.interaction):
    await interaction.response.send_message(f'{PONY_NAME}\'s water bucket is now full. {PRONOUNS[PONY_PRONOUN,0]} takes a nice long sip.')

@client.tree.command(name-"vet_care", description="Heal your pony. Services Menu: 1-Vaccines 2-Dental 3-Check up", guild=GUILD_ID)
async def vetServices(interaction: discord.interaction, vet_services: int):
    if vet_services = 1:
        await interaction.response.send_message(f'{PONY_NAME} stood for {PRONOUNS[PONY_PRONOUN,2]} shots. {PRONOUNS[PONY_PRONOUN,0]} were a very brave pony!')
    if vet_services = 2:
        await interaction.response.send_message(f'The dental floating went well. {PRONOUNS[PONY_PRONOUN,2]} teeth are nice and flat now, no more mouth issues for {PONY_NAME}!')
    if vet_services = 3:
        await interaction.response.send_message(f'The vet did a once over on {PONY_NAME}. They said {PONY_NAME} is the picture of health!')
    else:
        await interaction.response.send_message("The vet can't provide services if you don't select any. Please select a service from the list (1-3)")





client = Client(intents=intents)
client.run('')