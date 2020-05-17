import os
import asyncio
import discord
import traceback

from emoji import emojize
from time import sleep
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')


class DbDClient(discord.Client):
    def __init__(self):
        super().__init__()
        self.primary_guild = None
        self.roles = {}
        self.rule_msg = None
        self.members_added = 0


client = DbDClient()


async def logout():
    """D/c from Discord in 3"""
    print(f'Disconnecting in...')
    for i in range(3, 0, -1):
        print(f'{i}...')
        sleep(1)
    await client.logout()


@client.event
async def on_ready():
    """On connect, what do we do? Stuff and things"""
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Game('at the campfire...'))

    # Using Discord utils:  NOTE -- .get() builds a predicate for .find()
    guild = discord.utils.get(client.guilds, name=GUILD)
    client.primary_guild = guild

    client.roles.update({role.name: role for role in guild.roles})
    setattr(client, 'newcomer_roles', [client.roles['@everyone'],
                                       client.roles['newcomer']])

    print(f'{client.user} is connected to the following guild:\n'
          f'{guild.name} (id: {guild.id})')

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members: \n - {members}')

    # Get rules message
    rules = discord.utils.get(guild.channels, name='rules')
    rule_pins = await rules.pins()
    client.rules_msg = rule_pins[0]

    print(f'Ready to handle new members!')


@client.event
async def on_member_join(member):
    print(f'New member! {member}')
    guild = client.primary_guild
    await member.edit(roles=client.newcomer_roles)

    intros = discord.utils.get(guild.channels, name='introductions')
    spawn_point = discord.utils.get(guild.channels, name='spawn-point')
    rules = discord.utils.get(guild.channels, name='rules')

    await spawn_point.send(f'Welcome to the realm {member.mention}! \n'
                           f'Please read the rules to access the rest of the '
                           f'server: {rules.mention} \n'
                           f'Introduce yourself in the {intros.mention} '
                           f'channel and have fun!')


@client.event
async def on_error(event, *args, **kwargs):
    # Logging out on exception
    print(f'Exception! {emojize(":worried:", use_aliases=True)} {args}')
    print(traceback.format_exc())
    print('Logging out b/c of exception...')
    await logout()


@client.event
async def on_raw_reaction_add(payload):
    print(f'Handling reaction!: {payload}')

    def user_read_the_rules():
        if (payload.channel_id == client.rules_msg.channel.id and
                payload.message_id == client.rules_msg.id and
                payload.emoji.name == emojize(':thumbsup:', use_aliases=True)
                and payload.member.roles == client.newcomer_roles):
            return True

    if user_read_the_rules():
        # Update roles
        await payload.member.edit(roles=[client.roles['@everyone'],
                                         client.roles['normal']])
        print(f'Updated {payload.member} role to "normal"')
        client.members_added += 1

    if client.members_added == 1:
        print(f'Handled one member join! Logging out now...')
        await logout()

if __name__ == '__main__':
    try:
        asyncio.get_event_loop().run_until_complete(client.start(TOKEN))
    except KeyboardInterrupt:
        print('--------------- Manual Exit ---------------')
        asyncio.get_event_loop().run_until_complete(logout())
