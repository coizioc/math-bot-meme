"""Generates image macros from user-inputted text commands."""
import discord
from discord.ext import commands
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

RESOURCES_DIRECTORY = './subs/meme/resources/'
DRAKE_FILE = f'{RESOURCES_DIRECTORY}drake.jpg'
BOYFRIEND_FILE = f'{RESOURCES_DIRECTORY}distracted-bf.jpg'
EXIT_FILE = f'{RESOURCES_DIRECTORY}exit.jpg'
OUT_FILE = f'{RESOURCES_DIRECTORY}out.jpg'

# Distracted Boyfriend Area Coordinates
DISTRACTED_BF_COORDS = [(642, 279), (893, 366)]
DISTRACTED_GF_COORDS = [(901, 421), (1189, 562)]
DISTRACTED_GIRL_COORDS = [(179, 489), (485, 639)]

# Drake Area Coordinates
DRAKE_TOP_COORDS = [(333, 9), (630, 244)]
DRAKE_BOTTOM_COORDS = [(333, 272), (630, 540)]

# Left Exit 12 Area Coordinates
EXIT_STRAIGHT_COORDS = [(200, 103), (306, 294)]
EXIT_RIGHT_COORDS = [(412, 103), (576, 250)]
EXIT_CAR_COORDS = [(319, 508), (503, 624)]

AUTHORIZED_CHANNELS = [340426498764832768]

MAX_LINE_LENGTH = 16

BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)

PERMISSION_ERROR_STRING = f'Error: You do not have permission to use this command in this channel.'

class TextTooLongError(Exception):
    """Error raised for input that cannot fit within a bounded area with reasonably-sized text."""
    def __init__(self, text):
        self.text = text


def get_length(area):
    return area[1][0] - area[0][0]


def get_height(area):
    return area[1][1] - area[0][1]


def wrap_text(text, font, length=MAX_LINE_LENGTH):
    text_words = text.split(' ')
    text_line = ''
    new_text = []
    for word in text_words:
        if font.getsize(text_line + word)[0] <= length:
            text_line += word + ' '
        else:
            new_text.append(text_line)
            text_line = word + ' '
    else:
        if text_line != '':
            new_text.append(text_line)

    return '\n'.join(new_text)


def get_font_from_text(text, area, initial_size=36, fontname='arial'):
    font_size = initial_size
    while font_size > 11:
        font = ImageFont.truetype(f'{RESOURCES_DIRECTORY}{fontname}.ttf', font_size)
        area_dimensions = (get_length(area), get_height(area))
        new_text = wrap_text(text, font, area_dimensions[0])
        length = font.getsize(new_text.split('\n')[0])[0]
        lines = new_text.count('\n') + 1
        height = font.getsize(text)[1] * lines
        if length < area_dimensions[0] and height < area_dimensions[1]:
            return font
        font_size -= 2
    else:
        raise TextTooLongError(text[:100] + '...')


def place_text(file, texts, areas, initial_font_size=36, color=BLACK):
    image = Image.open(file)
    draw = ImageDraw.Draw(image)
    try:
        for text, area in zip(texts, areas):
            font = get_font_from_text(text, area, initial_size=initial_font_size)
            length = get_length(area)
            draw.text(area[0], wrap_text(text, font, length), color, font=font)
        image.save(OUT_FILE)
        return 'SUCCESS'
    except TextTooLongError as e:
        return f'Error: input too long ({e.text}).'


def variable_sized_comic(filename, texts, area_length, color=BLACK):
    if len(texts) > 11:
        return 'Error: too many args.'

    imagenames = [f"{RESOURCES_DIRECTORY}{filename}{i + 1}.jpg" for i in range(len(texts))]
    images = [Image.open(name) for name in imagenames]
    draws = [ImageDraw.Draw(image) for image in images]
    lengths, heights = zip(*(image.size for image in images))

    max_length = max(lengths)
    total_height = sum(heights)

    padding = 10

    for draw, text, image, height in zip(draws, texts, images, heights):
        font = get_font_from_text(text, [(padding, padding), (area_length - padding, height - padding)])
        draw.text((5, 5), wrap_text(text, font, area_length), color, font=font)

    full_image = Image.new('RGB', (max_length, total_height))

    y_offset = 0
    for image in images:
        full_image.paste(image, (0, y_offset))
        y_offset += image.size[1]

    full_image.save(OUT_FILE)
    return "SUCCESS"


class Meme():
    """Defines Meme commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def brain(self, ctx, *args):
        """Generates Expanding Brain image macro."""
        if ctx.channel.id in AUTHORIZED_CHANNELS:
            out = variable_sized_comic('brain', args, 300)
            if out == 'SUCCESS':
                await ctx.channel.send(file=discord.File(OUT_FILE))
            else:
                await ctx.channel.send(out)

    @commands.command()
    async def distracted_bf(self, ctx, bf, gf, girl):
        """Generates Distracted Boyfriend image macro."""
        if ctx.channel.id in AUTHORIZED_CHANNELS:
            texts = [bf, gf, girl]
            areas = [DISTRACTED_BF_COORDS, DISTRACTED_GF_COORDS, DISTRACTED_GIRL_COORDS]
            out = place_text(BOYFRIEND_FILE, texts, areas, initial_font_size=60)
            if out == 'SUCCESS':
                await ctx.channel.send(file=discord.File(OUT_FILE))
            else:
                await ctx.channel.send(out)

    @commands.command()
    async def drake(self, ctx, top, bottom):
        """Generates Drakeposting image macro."""
        if ctx.channel.id in AUTHORIZED_CHANNELS:
            texts = [top, bottom]
            areas = [DRAKE_TOP_COORDS, DRAKE_BOTTOM_COORDS]
            out = place_text(DRAKE_FILE, texts, areas)
            if out == 'SUCCESS':
                await ctx.channel.send(file=discord.File(OUT_FILE))
            else:
                await ctx.channel.send(out)

    @commands.command()
    async def exit(self, ctx, straight, right, car):
        """Generates Left Exit 12 Off Ramp image macro."""
        if ctx.channel.id in AUTHORIZED_CHANNELS:
            texts = [straight, right, car]
            areas = [EXIT_STRAIGHT_COORDS, EXIT_RIGHT_COORDS, EXIT_CAR_COORDS]
            out = place_text(EXIT_FILE, texts, areas, color=WHITE, initial_font_size=60)
            if out == 'SUCCESS':
                await ctx.channel.send(file=discord.File(OUT_FILE))
            else:
                await ctx.channel.send(out)


def setup(bot):
    """Adds the cog to the bot."""
    bot.add_cog(Meme(bot))
