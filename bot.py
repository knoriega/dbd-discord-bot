import os
import asyncio
import discord
import functools

from time import sleep
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


class RuntimeAttrs:
    def __init__(self):
        pass


client = discord.Client()
setattr(client, 'runtime_attr', RuntimeAttrs())


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
    roles = guild.roles

    print(f'{client.user} is connected to the following guild:\n'
          f'{guild.name} (id: {guild.id})')

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members: \n - {members}')

    # Set runtime attrs
    setattr(client.runtime_attr, 'members_joined', 0)
    setattr(client.runtime_attr, 'primary_guild', guild)
    setattr(client.runtime_attr, 'roles', roles)
    print(f'Ready to handle new members!')


@client.event
@logout_on_exception
async def on_member_join(member):
    await member.edit(roles=client.runtime_attr.roles[:2])  # Set to newcomer
    rules = discord.utils.get(client.runtime_attr.primary_guild.channels,
                              name='rules')

    intros = discord.utils.get(client.runtime_attr.primary_guild.channels,
                               name='introductions')

    spawn_point = discord.utils.get(client.runtime_attr.primary_guild.channels,
                                    name='spawn-point')

    await spawn_point.send(f'Welcome to the realm {member.mention}! \n'
                           f'Please read the rules to access the rest of the server: {rules.mention} \n'
                           f'Introduce yourself in the {intros.mention} channel and have fun!')

    client.runtime_attr.members_joined += 1
    if client.runtime_attr.members_joined == 1:
        print(f'Handled one member join! Logging out now...')
        await logout(client)

# TODO: New member w/ 'newcomer' role must react to rules to be upgraded


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(client.start(TOKEN))
