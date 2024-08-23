from discord.ext import commands
from loguru import logger
from discord.ext.commands.context import Context
from discord.ext.commands.bot import Bot
from PIL import Image, ImageDraw
import io
import os
import discord

class Jacket(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info(f"{__name__} is online")

    def jacket_files(self):
        path = os.path.realpath(os.path.dirname(__file__)) + os.path.sep
        jacket_image = path + "jacket.png"
        jacket_text = path + "jacket_text.png"

        return {"image": jacket_image, "text_image": jacket_text}

    def jacket_colors(self):
        gold_color = (255, 223, 0, 255) # Gold with no Alpha Transparency
        white_color = (255, 255, 255, 255) # Full White with no Alpha transparency

        return {"background": white_color, "txt_background": gold_color}

    def create_jacket(self, certs: list[str]):
        jacket_pieces = [
            ((150, 50), ["SAP"]),
            ((300, 50), ["DOP"]),
            ((70, 150), ["DBS"]),
            ((150, 150), ["ANS", "NETWORKING"]),
            ((300, 150), ["SCS"]),
            ((380, 150), ["DAS"]),
            ((150, 250), ["DVA"]),
            ((300, 250), ["SOA"]),
            ((30, 350), ["MLS"]),
            ((150, 350), ["CLF", "CCP"]),
            ((300, 350), ["SAA"]),
            ((415, 350), ["PAS"]),
        ]

        certs = [cert.upper() for cert in certs]
        jacket = Image.open(self.jacket_files()['image']).convert("RGBA")

        for location, names in jacket_pieces:
            color = self.jacket_colors()['background']

            if any(name in certs for name in names):
                color = self.jacket_colors()['txt_background']

            ImageDraw.floodfill(
                image=jacket,
                xy=location,
                value=color
            )

        # Overlay the text on the image
        text_layer = Image.open(self.jacket_files()['text_image']).convert("RGBA")
        jacket.paste(text_layer, (0, 0), text_layer)

        # Filters we can add for fun
        # Remember to import ImageFilter
        # jacket = jacket.filter(ImageFilter.UnsharpMask) #  https://pillow.readthedocs.io/en/stable/reference/ImageFilter.html

        # Convert the image to RGB by creating a white background and compositing
        background = Image.new("RGB", jacket.size, (255, 255, 255))  # White background
        jacket_rgb = Image.alpha_composite(background.convert("RGBA"), jacket)
        # jacket_rgb.save("testing_alpha.webp", format="WEBP", quality=90)

        # Save the final image to a bytes buffer as WebP
        image_byte_array = io.BytesIO()
        jacket_rgb.save(image_byte_array, format="WEBP", quality=90)
        image_byte_array.seek(0)

        return image_byte_array

    @commands.command()
    async def jacket(self, ctx: Context, *args):
        if len(args) < 1:
            await ctx.send("Example: !jacket SAP DOP DBS ANS NETWORKING SCS DAS DVA SOA MLS CLF CCP SAA PAS ")
            return

        if args[0].lower() == "help":
            await ctx.send("Example: !jacket SAP DOP DBS ANS NETWORKING SCS DAS DVA SOA MLS CLF CCP SAA PAS ")
            return

        image_bytes = self.create_jacket(args)
        image_file_send = discord.File(fp=image_bytes, filename="aws-jacket.webp")
        await ctx.send("<:golden_jacket:1014289794630697023>  One AWS Golden Jacket coming up! <:golden_jacket:1014289794630697023> ", file=image_file_send)

async def setup(bot):
    await bot.add_cog(Jacket(bot))
