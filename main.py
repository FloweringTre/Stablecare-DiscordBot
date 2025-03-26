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

client = Client(intents=intents)
client.run('')