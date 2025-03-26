import discord

class Client(discord.Client):
    async def on_ready(self):
        print(f'Successfully connected as {self.user}.')
    
    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')
    
    

intents = discord.Intents.default()
intents.message_content = True

client = Client(intents=intents)
client.run('MTM1NDI4OTY1OTUxNzA3NTUzOA.GHXmTU.aqvjws_v3TBG_R9GZ-KupzMEW7MLFERIvXSt6c')