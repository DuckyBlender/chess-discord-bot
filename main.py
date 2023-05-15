# Template discord bot

import discord
from discord.ext import commands
import os
import random

# Bot prefix
client = commands.Bot(command_prefix=".")
# Bot token
token = os.getenv("DISCORD_TOKEN")


# Bot is ready
@client.event
async def on_ready():
    print("Bot is ready.")
