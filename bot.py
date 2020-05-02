import os

import discord
from time import sleep
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()


@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    print(f'Disconnecting in...')
    for i in range(5, 0, -1):
        print(f'{i}...')
        sleep(1)

    await client.logout()

if __name__ == '__main__':
    client.run(TOKEN)
