"""Generates image macros from user-inputted text commands."""
import discord
from discord.ext import commands
from io import BytesIO
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import random
import requests

RESOURCES_DIRECTORY = './subs/meme/resources/'
BOARDROOM_FILE = f'{RESOURCES_DIRECTORY}boardroom.jpg'
BREAKING_NEWS_FILE = f'{RESOURCES_DIRECTORY}breakingnews.png'
BOYFRIEND_FILE = f'{RESOURCES_DIRECTORY}distracted-bf.jpg'
DRAKE_FILE = f'{RESOURCES_DIRECTORY}drake.jpg'
EXIT_FILE = f'{RESOURCES_DIRECTORY}exit.jpg'
MOCKING_SPONGEBOB_FILE = f'{RESOURCES_DIRECTORY}mockingspongebob.jpg'
ROLL_SAFE_FILE = f'{RESOURCES_DIRECTORY}rollsafe.jpg'
SONIC_FILE = f'{RESOURCES_DIRECTORY}sonicsays.jpg'
SCROLL_OF_TRUTH_FILE = f'{RESOURCES_DIRECTORY}scrolloftruth.jpg'

OUT_FILE = f'{RESOURCES_DIRECTORY}out.jpg'

# Breaking News Area Coordinates
NEWS_HEADLINE_COORDS = [(68, 316), (755, 351)]
NEWS_TICKER_COORDS = [(113, 372), (755, 394)]

# Boardroom Suggestion Area Coordinates
BOARDROOM_BOSS_COORDS = [(155, 8), (452, 51)]
BOARDROOM_GUY1_COORDS = [(26, 249), (122, 274)]
BOARDROOM_WOMAN_COORDS = [(162, 256), (245, 283)]
BOARDROOM_GUY2_COORDS = [(307, 259), (437, 303)]

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

# Mocking Spongebob Coordinates
SPONGEBOB_TOP_COORDS = [(20, 20), (980, 110)]
SPONGEBOB_BOTTOM_COORDS = [(20, 130), (980, 230)]

# Roll Safe Coordinates
ROLL_SAFE_COORDS = [(15, 15), (560, 63)]

# Scroll of Truth Coordinates
SCROLL_COORDS = [(242, 714), (473,1000)]

# Sonic Says Area Coordinates
SONIC_COORDS = [(89, 70), (269, 194)]

AUTHORIZED_CHANNELS = [340426498764832768, 408424622648721410, 340426332859269140]

MAX_LINE_LENGTH = 16
MINIMUM_FONT_SIZE = 6

SUCCESS_STRING = 'SUCCESS'

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


def get_font_from_text(text, area, fontname, initial_size=36):
    font_size = initial_size
    while font_size >= MINIMUM_FONT_SIZE:
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


def place_text(file, texts, areas, initial_font_size=36, color=BLACK, fontname='arial'):
    image = Image.open(file)
    draw = ImageDraw.Draw(image)
    try:
        for text, area in zip(texts, areas):
            font = get_font_from_text(text, area, fontname, initial_size=initial_font_size)
            length = get_length(area)
            draw.text(area[0], wrap_text(text, font, length), color, font=font)
        image.save(OUT_FILE)
        return SUCCESS_STRING
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

    padding = 20

    for draw, text, image, height in zip(draws, texts, images, heights):
        font = get_font_from_text(text, [(padding, padding), (area_length - padding, height - padding)], 'arial')
        draw.text((5, 5), wrap_text(text, font, area_length), color, font=font)

    full_image = Image.new('RGB', (max_length, total_height))

    y_offset = 0
    for image in images:
        full_image.paste(image, (0, y_offset))
        y_offset += image.size[1]

    full_image.save(OUT_FILE)
    return SUCCESS_STRING


def place_overlay_on_image(image_url, overlay):
    try:
        bg_image = Image.open(BytesIO(requests.get(image_url).content))
    except:
        return 'Error: no image in URL or invalid URL.'

    overlay_image = Image.open(overlay)

    bg_image = bg_image.resize(overlay_image.size, Image.ANTIALIAS)
    bg_image.paste(overlay_image, mask=overlay_image)
    bg_image.save(OUT_FILE)

    return SUCCESS_STRING


class Meme():
    """Defines Meme commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['boardroom'])
    async def boardroom_suggestion(self, ctx, boss, guy1, woman, guy2):
        """Generates Boardroom Suggestion image macro."""
        if ctx.channel.id in AUTHORIZED_CHANNELS:
            texts = [boss, guy1, woman, guy2]
            areas = [BOARDROOM_BOSS_COORDS, BOARDROOM_GUY1_COORDS, BOARDROOM_WOMAN_COORDS, BOARDROOM_GUY2_COORDS]
            out = place_text(BOARDROOM_FILE, texts, areas, initial_font_size=60)
            if out == SUCCESS_STRING:
                await ctx.channel.send(file=discord.File(OUT_FILE))
            else:
                await ctx.channel.send(out)

    @commands.command()
    async def brain(self, ctx, *args):
        """Generates Expanding Brain image macro."""
        if ctx.channel.id in AUTHORIZED_CHANNELS:
            out = variable_sized_comic('brain', args, 300)
            if out == SUCCESS_STRING:
                await ctx.channel.send(file=discord.File(OUT_FILE))
            else:
                await ctx.channel.send(out)

    @commands.command(aliases=['news', 'despacito'])
    async def breaking_news(self, ctx, image_url, headline, ticker):
        """Generates Breaking News image macro."""
        if ctx.channel.id in AUTHORIZED_CHANNELS:
            out = place_overlay_on_image(image_url, BREAKING_NEWS_FILE)
            if out == SUCCESS_STRING:
                texts = [headline.upper(), ticker.upper()]
                areas = [NEWS_HEADLINE_COORDS, NEWS_TICKER_COORDS]
                out = place_text(OUT_FILE, texts, areas, fontname='Signika-bold')
                if out == SUCCESS_STRING:
                    await ctx.channel.send(file=discord.File(OUT_FILE))
                else:
                    await ctx.channel.send(out)
            else:
                await ctx.channel.send(out)

    @commands.command(aliases=['bf', 'boyfriend'])
    async def distracted_bf(self, ctx, bf, gf, girl):
        """Generates Distracted Boyfriend image macro."""
        if ctx.channel.id in AUTHORIZED_CHANNELS:
            texts = [bf, gf, girl]
            areas = [DISTRACTED_BF_COORDS, DISTRACTED_GF_COORDS, DISTRACTED_GIRL_COORDS]
            out = place_text(BOYFRIEND_FILE, texts, areas, initial_font_size=60)
            if out == SUCCESS_STRING:
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
            if out == SUCCESS_STRING:
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
            if out == SUCCESS_STRING:
                await ctx.channel.send(file=discord.File(OUT_FILE))
            else:
                await ctx.channel.send(out)

    @commands.command(aliases=['spongebob'])
    async def mocking_spongebob(self, ctx, person1, person2, message):
        """Generates Mocking Spongebob image macro."""
        if ctx.channel.id in AUTHORIZED_CHANNELS:
            submessage1 = person1 + ': ' + message
            message = ''.join(random.choice([char.upper(), char]) for char in message)
            submessage2 = person2 + ': ' + message
            texts = [submessage1, submessage2]
            areas = [SPONGEBOB_TOP_COORDS, SPONGEBOB_BOTTOM_COORDS]
            out = place_text(MOCKING_SPONGEBOB_FILE, texts, areas, initial_font_size=60)
            if out == SUCCESS_STRING:
                await ctx.channel.send(file=discord.File(OUT_FILE))
            else:
                await ctx.channel.send(out)

    @commands.command()
    async def roll_safe(self, ctx, message):
        """Generates Roll Safe image macro."""
        if ctx.channel.id in AUTHORIZED_CHANNELS:
            texts = [message]
            areas = [ROLL_SAFE_COORDS]
            out = place_text(ROLL_SAFE_FILE, texts, areas)
            if out == SUCCESS_STRING:
                await ctx.channel.send(file=discord.File(OUT_FILE))
            else:
                await ctx.channel.send(out)

    @commands.command(aliases=['scroll'])
    async def truth(self, ctx, message):
        """Generates The Scroll of Truth image macro."""
        if ctx.channel.id in AUTHORIZED_CHANNELS:
            texts = [message]
            areas = [SCROLL_COORDS]
            out = place_text(SCROLL_OF_TRUTH_FILE, texts, areas)
            if out == SUCCESS_STRING:
                await ctx.channel.send(file=discord.File(OUT_FILE))
            else:
                await ctx.channel.send(out)

    @commands.command(aliases=['sonic'])
    async def sonic_says(self, ctx, message):
        """Generates Sonic Says image macro."""
        if ctx.channel.id in AUTHORIZED_CHANNELS:
            texts = [message]
            areas = [SONIC_COORDS]
            out = place_text(SONIC_FILE, texts, areas, color=WHITE)
            if out == SUCCESS_STRING:
                await ctx.channel.send(file=discord.File(OUT_FILE))
            else:
                await ctx.channel.send(out)


def setup(bot):
    """Adds the cog to the bot."""
    bot.add_cog(Meme(bot))
