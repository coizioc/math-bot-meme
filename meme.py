"""Generates image macros from user-inputted text commands."""
import discord
from discord.ext import commands
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

RESOURCES_DIRECTORY = './subs/meme/resources/'
DRAKE_FILE = f'{RESOURCES_DIRECTORY}drake.jpg'
BOYFRIEND_FILE = f'{RESOURCES_DIRECTORY}distracted-bf.jpg'
OUT_FILE = f'{RESOURCES_DIRECTORY}out.jpg'

DEFAULT_FONT = ImageFont.truetype(f'{RESOURCES_DIRECTORY}arial.ttf', 32)

MAX_LINE_LENGTH = 16

BLACK = (0, 0, 0)

def wrap_text(text):
    text_words = text.split(' ')
    text_line = ''
    new_text = []
    for word in text_words:
        if len(text_line) + len(word) <= MAX_LINE_LENGTH:
            text_line += word + ' '
        else:
            new_text.append(text_line)
            text_line = word + ' '
    else:
        if text_line != '':
            new_text.append(text_line)

    return '\n'.join(new_text)


class Meme():
    """Defines Casal commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def drake(self, ctx, top, bottom):
        drake_image = Image.open(DRAKE_FILE)
        draw = ImageDraw.Draw(drake_image)
        draw.text((355, 30), wrap_text(top), BLACK, font=DEFAULT_FONT)
        draw.text((355, 300), wrap_text(bottom), BLACK, font=DEFAULT_FONT)
        drake_image.save(OUT_FILE)
        await ctx.channel.send(file=discord.File(OUT_FILE))

    @commands.command()
    @commands.is_owner()
    async def distracted_bf(self, ctx, bf, gf, girl):
        boyfriend_image = Image.open(BOYFRIEND_FILE)
        draw = ImageDraw.Draw(boyfriend_image)
        draw.text((660, 295), wrap_text(bf), BLACK, font=DEFAULT_FONT)
        draw.text((920, 444), wrap_text(gf), BLACK, font=DEFAULT_FONT)
        draw.text((202, 512), wrap_text(girl), BLACK, font=DEFAULT_FONT)
        boyfriend_image.save(OUT_FILE)
        await ctx.channel.send(file=discord.File(OUT_FILE))

def setup(bot):
    """Adds the cog to the bot."""
    bot.add_cog(Meme(bot))
