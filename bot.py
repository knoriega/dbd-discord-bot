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

client = discord.Client()

# Properties -- Initialized here, use in a proper bot class later
guilds = {}
roles = {}  # Key: role names, Value: role objects
channels = {}
rules_msg = []
members = []


async def logout():
    """D/c from Discord in 5"""
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
    guilds['primary'] = guild

    roles.update({role.name: role for role in guild.roles})

    print(f'{client.user} is connected to the following guild:\n'
          f'{guild.name} (id: {guild.id})')

    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members: \n - {members}')

    # Get rules message
    rules = discord.utils.get(guild.channels, name='rules')
    channels['rules'] = rules
    rule_pins = await rules.pins()
    rules_msg.append(rule_pins[0])

    print(f'Ready to handle new members!')


@client.event
async def on_member_join(member):
    await member.edit(roles=[roles['@everyone'], roles['newcomer']])
    guild = guilds['primary']

    intros = discord.utils.get(guild.channels, name='introductions')
    spawn_point = discord.utils.get(guild.channels, name='spawn-point')

    await spawn_point.send(f'Welcome to the realm {member.mention}! \n'
                           f'Please read the rules to access the rest of the '
                           f'server: {channels["rules"].mention} \n'
                           f'Introduce yourself in the {intros.mention} '
                           f'channel and have fun!')

    members.append(member)


@client.event
async def on_error(event, *args, **kwargs):
    # Logging out on exception
    print(f'Exception! {emojize(":worried:", use_aliases=True)} {args}')
    print(traceback.format_exc())
    print('Logging out b/c of exception...')
    await logout()


# TODO: New member w/ 'newcomer' role must react to rules to be upgraded


@client.event
async def on_raw_reaction_add(payload):
    print(f'Handling reaction!: {payload}')
    newcomer_roles = [roles['@everyone'], roles['newcomer']]
    msg = rules_msg[0]

    def msg_check():
        if (payload.channel_id == msg.channel.id and
                payload.message_id == msg.id and
                payload.emoji.name == emojize(':thumbsup:', use_aliases=True)
                and payload.member.roles == newcomer_roles):
            return True

    if msg_check():
        # Update roles
        await payload.member.edit(roles=[roles['@everyone'], roles['normal']])
        print(f'Updated {payload.member} role to "normal"')

        if len(members) == 1:
            print(f'Handled one member join! Logging out now...')
            await logout()

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(client.start(TOKEN))
