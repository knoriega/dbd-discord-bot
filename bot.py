import os
import asyncio
import discord
import functools

from time import sleep
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()


class RuntimeAttrs:
    def __init__(self):
        pass


def logout_on_exception(func):
    """Try-catch block for async Discord callbacks"""
    @functools.wraps(func)
    async def wrapper_decorator(*args, **kwargs):
        try:
            value = await func(*args, **kwargs)
            return value
        except Exception as err:
            print(f'Error occurred! -- {err}')
            print(f'Logging out now...')
            await client.logout()

    return wrapper_decorator


async def logout(client):
    """D/c from Discord in 5"""
    print(f'Disconnecting in...')
    for i in range(5, 0, -1):
        print(f'{i}...')
        sleep(1)
    await client.logout()


@client.event
@logout_on_exception
async def on_ready():

    """On connect, what do we do? Stuff and things"""
    print(f'{client.user} has connected to Discord!')

    # Using Discord utils:  NOTE -- .get() builds a predicate for .find()
    guild = discord.utils.get(client.guilds, name=GUILD)

    print(f'{client.user} is connected to the following guild:\n'
          f'{guild.name} (id: {guild.id})')

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members: \n - {members}')

    # Set runtime attrs
    setattr(client, 'runtime_attr', RuntimeAttrs())
    setattr(client.runtime_attr, 'members_joined', 0)
    setattr(client.runtime_attr, 'primary_guild', guild)
    print(f'Ready to handle new members!')


@client.event
@logout_on_exception
async def on_member_join(member):
    rules = discord.utils.get(client.runtime_attr.primary_guild.channels,
                              name='rules')

    await member.create_dm()
    dm = member.dm_channel
    await dm.send(f'Welcome to the realm {member.mention}! '
                  f'Please read the rules before entering: {rules.mention}')

    client.runtime_attr.members_joined += 1
    if client.runtime_attr.members_joined == 1:
        print(f'Handled one member join! Logging out now...')
        await logout(client)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(client.start(TOKEN))
