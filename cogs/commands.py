import discord
import asyncpraw
import requests
import json
from discord.ext.tasks import *
from discord.ext.commands import *

with open("config.json", "r") as f:
    config = json.load(f)

reddit = asyncpraw.Reddit(
    user_agent=config["reddit"]["user_agent"],
    client_id=config["reddit"]["client_id"],
    client_secret=config["reddit"]["client_secret"],
    username=config["reddit"]["username"],
    password=config["reddit"]["password"]
)

class Help(MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page)
            await destination.send(embed=emby)

    def get_opening_note(self):
        return "Tee 'lk help [komento]' saadaksesi lisätietoja komennosta."


class Commands(Cog, name='Komennot'):
    def __init__(self, bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = Help()
        bot.help_command.cog = self

    @command(brief='Poistaa viestejä.')
    @has_permissions(manage_messages=True)
    async def poista(self, ctx, amount=1):
        await ctx.channel.purge(limit=amount+1)
        await ctx.channel.send(content='{} viestiä poistettu.'.format(amount), delete_after=5)

    @command()
    async def meme(self, ctx):
        subreddit = await reddit.subreddit("LakkoPostaukset")
        submission = await get_image(subreddit, ["Meemit", "LakkoMeemit"])
        await submission.author.load()

        e = discord.Embed(title=submission.title, color=0x11ff11)
        e.set_image(url=submission.url)
        e.set_footer(text="u/" + submission.author.name,
                     icon_url=submission.author.icon_img)

        await ctx.channel.send(embed=e)
    
    @command()
    async def fanart(self, ctx):
        subreddit = await reddit.subreddit("LakkoPostaukset")
        submission = await get_image(subreddit, ["FanArt"])
        await submission.author.load()

        e = discord.Embed(title=submission.title, color=0x11ff11)
        e.set_image(url=submission.url)
        e.set_footer(text="u/" + submission.author.name,
                     icon_url=submission.author.icon_img)

        await ctx.channel.send(embed=e)
    
    @command(brief='Tarkistaa kryptovaluutan hinnan')
    async def crypto(self, ctx, valuutta: str):
        valuutta = valuutta.lower()
        url = 'https://api.coingecko.com/api/v3/simple/price?ids=' + \
            valuutta + '&vs_currencies=eur'
        r = requests.get(url)
        value = r.json()[valuutta]["eur"]
        await ctx.message.channel.send("Yksi {} = {}€".format(valuutta.replace("-", " ").title(), value))


async def get_image(sub, flairs):
    s = await sub.random()
    if not s.is_self:
        if s.link_flair_text in flairs:
            return s
        else:
            return await get_image(sub, flairs)
    else:
        return await get_image(sub, flairs)


def setup(bot):
    bot.add_cog(Commands(bot))
