import discord
import os
import asyncpraw
import json
import requests
from datetime import date
from discord.ext.tasks import *
from discord.ext.commands import *
from discord.ext.commands.errors import *
from itertools import cycle

BOT_PREFIX = ['lk ', 'Lk ', 'LK ', 'lK']
client = discord.ext.commands.Bot(
    command_prefix=BOT_PREFIX, case_insensitive=True, help_command=None)

with open('status.txt', 'r') as f:
    st = f.read().splitlines()
status = cycle(st)

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

with open("config.json", "r") as f:
    config = json.load(f)

@loop(minutes=1)
async def change_status():
    activity = discord.Activity(
        name=(next(status)), type=discord.ActivityType.playing)
    await client.change_presence(activity=activity)

@loop(minutes=1)
async def check_video():
    with open("r.json", "r") as f:
        v = json.load(f)

    video_id = v['items'][0]['contentDetails']['upload']['videoId']

    apiKey = config['yt_api']
    r = requests.get("https://www.googleapis.com/youtube/v3/activities?part=contentDetails,id&channelId=UC1BIOZPjE3lYa2s3ZT1kYaA&maxResults=1&key=" + apiKey)

    with open("r.json", "w") as f:
        json.dump(r.json(), f, indent=4)
    
    new_video_id = r.json()['items'][0]['contentDetails']['upload']['videoId']
    
    if video_id != new_video_id:
        channel = client.get_channel(config["notifications"])
        await channel.send(content="**Lakko latasi uuden videon!**\n\nKatso se tästä: https://youtu.be/" + new_video_id)


@loop(hours=24)
async def top():
    reddit = asyncpraw.Reddit(
        user_agent=config["reddit"]["user_agent"],
        client_id=config["reddit"]["client_id"],
        client_secret=config["reddit"]["client_secret"],
        username=config["reddit"]["username"],
        password=config["reddit"]["password"]
    )

    channel = client.get_channel(config["lk"])
    subreddit = await reddit.subreddit("LakkoPostaukset")
    posts = subreddit.top("day", limit=1)

    async for p in posts:
        await p.author.load()
        e = discord.Embed(title="Viimeisen 24h paras postaus - " +
                          str(date.today()), description=p.title, color=0x11ff11)
        e.set_image(url=p.url)
        e.set_footer(text="u/" + p.author.name,
                     icon_url=p.author.icon_img)

        await channel.send(embed=e)

    await reddit.close()


@client.event
async def on_ready():
    change_status.start()
    top.start()
    check_video.start()
    print(f'Logged in as {client.user}')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.channel.send(content="Sinulla ei ole riittäviä oikeuksia komennon suorittamiseen", delete_after=10)
    elif isinstance(error, MissingRequiredArgument):
        await ctx.channel.send(content="Lisää puuttuva parametri", delete_after=10)
    elif isinstance(error, BotMissingPermissions):
        await ctx.channel.send(content="Botilla ei ole riittäviä oikeuksia komennon suorittamiseen.", delete_after=10)
    elif isinstance(error, KeyError):
        await ctx.channel.send(content="Avainta ei löydy.", delete_after=10)
    else:
        print(error)
    pass


@client.event
async def on_message(message):
    if message.author.bot == False:
        if "uwu" in str.lower(message.content):
            await message.channel.send(content='Warning, the Council of High Intelligence and Educational Findings (C.H.I.E.F.), has detected an "uwu". This is a code BRUH #4 level threat. Stay indoors and do not interact with cringe weebs until the threat has been classified as "it". Unless the code BRUH is retracted, "uwu" will be classified under "not it" until further notice.')
        elif "owo" in str.lower(message.content):
            await message.channel.send(content='Warning, the Council of High Intelligence and Educational Findings (C.H.I.E.F.), has detected an "owo". This is a code BRUH #4 level threat. Stay indoors and do not interact with cringe weebs until the threat has been classified as "it". Unless the code BRUH is retracted, "owo" will be classified under "not it" until further notice.')
        if message.channel.id in config["channels"]:
            try:
                await client.process_commands(message)
            except Exception as e:
                message.channel.send(e)

client.run(config["dc_api"])
