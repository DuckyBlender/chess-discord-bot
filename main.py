from datetime import datetime, timedelta
import discord
from discord import app_commands
import aiohttp

from dotenv import load_dotenv
import os

load_dotenv()


MY_GUILD = discord.Object(id=1100504969746071602)  # replace with your guild id


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")
    print("------")


@client.tree.command()
async def ping(interaction: discord.Interaction):
    """
    Get the latency of the bot
    """
    # create embed
    embed = discord.Embed(
        title="Pong!",
        description=f"Discord API latency: `{round(client.latency * 1000)}ms`",
        color=0x00FF00,
    )
    # send embed
    await interaction.response.send_message(
        embed=embed,
        ephemeral=True,
    )


@client.tree.command()
async def nick(interaction: discord.Interaction, username: str):
    """
    Change your nickname to your chess.com username with your rating
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.chess.com/pub/player/{username}/stats"
        ) as resp1:
            if resp1.status == 301 or resp1.status == 404:
                # create embed
                embed = discord.Embed(
                    title="User not found",
                    description="The user you are looking for doesn't exist",
                    color=0xFF0000,
                )
                # send embed
                return await interaction.response.send_message(
                    embed=embed,
                )
            async with session.get(
                f"https://api.chess.com/pub/player/{username}"
            ) as resp2:
                if resp1.status == 429 or resp2.status == 429:
                    # create embed
                    embed = discord.Embed(
                        title="Rate limit exceeded",
                        description="Please try again later",
                        color=0xFF0000,
                    )
                    # send embed
                    return await interaction.response.send_message(
                        embed=embed,
                        ephemeral=True,
                    )

                if resp1.status != 200 or resp2.status != 200:
                    # create embed
                    embed = discord.Embed(
                        title="An error occured",
                        description="Please try again later",
                        color=0xFF0000,
                    )
                    # send embed
                    return await interaction.response.send_message(
                        embed=embed,
                        ephemeral=True,
                    )

                stats = await resp1.json()
                profile = await resp2.json()
                # Update the users discord nickname
                # the only way to get properly capitalised username is to get it from the profile url
                username = profile["url"].split("/")[-1]

                member = await interaction.guild.fetch_member(interaction.user.id)
                try:
                    await member.edit(
                        nick=f"{username} ({stats['chess_rapid']['last']['rating']})"
                    )
                    # create embed
                    embed = discord.Embed(
                        title="Nickname changed",
                        description=f"Your nickname has been changed to `{username} ({stats['chess_rapid']['last']['rating']})`",
                        color=0x00FF00,
                    )
                    return await interaction.response.send_message(
                        embed=embed,
                        ephemeral=True,
                    )

                except discord.Forbidden:
                    # create embed
                    embed = discord.Embed(
                        title="Nickname not changed",
                        description="I don't have permission to change your nickname",
                        color=0xFF0000,
                    )
                    return await interaction.response.send_message(
                        embed=embed,
                        ephemeral=True,
                    )


@client.tree.command()
@app_commands.describe(
    username="The username of the user you want to get the stats from"
)
async def chess(interaction: discord.Interaction, username: str):
    """
    Get the general stats of a user
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.chess.com/pub/player/{username}/stats"
        ) as resp1:
            if resp1.status == 301 or resp1.status == 404:
                # create embed
                embed = discord.Embed(
                    title="User not found",
                    description="The user you are looking for doesn't exist",
                    color=0xFF0000,
                )
                # send embed
                return await interaction.response.send_message(
                    embed=embed,
                )
            async with session.get(
                f"https://api.chess.com/pub/player/{username}"
            ) as resp2:
                if resp1.status == 429 or resp2.status == 429:
                    # create embed
                    embed = discord.Embed(
                        title="Rate limit exceeded",
                        description="Please try again later",
                        color=0xFF0000,
                    )
                    # send embed
                    return await interaction.response.send_message(
                        embed=embed,
                        ephemeral=True,
                    )

                if resp1.status != 200 or resp2.status != 200:
                    # create embed
                    embed = discord.Embed(
                        title="An error occured",
                        description="Please try again later",
                        color=0xFF0000,
                    )
                    # send embed
                    return await interaction.response.send_message(
                        embed=embed,
                        ephemeral=True,
                    )

                stats = await resp1.json()
                profile = await resp2.json()
                # Update the users discord nickname
                # the only way to get properly capitalised username is to get it from the profile url
                username = profile["url"].split("/")[-1]

                # member = await interaction.guild.fetch_member(interaction.user.id)
                # try:
                #     await member.edit(
                #         nick=f"{username} ({stats['chess_rapid']['last']['rating']})"
                #     )
                # except discord.Forbidden:
                #     # return await interaction.response.send_message(
                #     #     "I don't have permission to change your nickname"
                #     # )
                #     print(f"I don't have permission to change {member}'s nickname")

                joined = profile["joined"]
                # convert unix timestamp to datetime
                joined = datetime.fromtimestamp(joined)
                # format the datetime
                joined = joined.strftime(f"%d.%m.%Y")

                # country
                country = profile["country"]
                # strip the country code from the url
                country = country.split("/")[-1]

                try:
                    last_online = profile["last_online"]
                    # convert unix timestamp to datetime
                    last_online = datetime.fromtimestamp(last_online)
                    # compare the last online date to the current date. if the user is online 5 minutes ago, he is online
                    if last_online > datetime.now() - timedelta(minutes=5):
                        last_online = "Online"
                    else:
                        # format the datetime, for example: 10 minutes ago
                        last_online = last_online.strftime(f"%d.%m.%Y %H:%M:%S")
                except KeyError:
                    last_online = "Unknown"

                # Form the embed using the two JSON responses
                embed = discord.Embed(
                    title=f"{username}'s chess.com profile",
                    description=f"**Joined:** `{joined}`\n**Country:** `{country}`\n**Last online:** `{last_online}`",
                    color=0x00FF00,
                )

                # profile picture
                embed.set_thumbnail(url=profile["avatar"])

                # rapid
                try:
                    embed.add_field(
                        name="Rapid",
                        value=f"Rating: `{stats['chess_rapid']['last']['rating']}`\nBest rating: `{stats['chess_rapid']['best']['rating']}`\nGames played: `{stats['chess_rapid']['record']['win'] + stats['chess_rapid']['record']['loss'] + stats['chess_rapid']['record']['draw']}`\nWins: `{stats['chess_rapid']['record']['win']}`\nLosses: `{stats['chess_rapid']['record']['loss']}`\nDraws: `{stats['chess_rapid']['record']['draw']}`",
                    )
                except KeyError:
                    pass

                # blitz
                try:
                    embed.add_field(
                        name="Blitz",
                        value=f"Rating: `{stats['chess_blitz']['last']['rating']}`\nBest rating: `{stats['chess_blitz']['best']['rating']}`\nGames played: `{stats['chess_blitz']['record']['win'] + stats['chess_blitz']['record']['loss'] + stats['chess_blitz']['record']['draw']}`\nWins: `{stats['chess_blitz']['record']['win']}`\nLosses: `{stats['chess_blitz']['record']['loss']}`\nDraws: `{stats['chess_blitz']['record']['draw']}`",
                    )
                except KeyError:
                    pass

                # bullet
                try:
                    embed.add_field(
                        name="Bullet",
                        value=f"Rating: `{stats['chess_bullet']['last']['rating']}`\nBest rating: `{stats['chess_bullet']['best']['rating']}`\nGames played: `{stats['chess_bullet']['record']['win'] + stats['chess_bullet']['record']['loss'] + stats['chess_bullet']['record']['draw']}`\nWins: `{stats['chess_bullet']['record']['win']}`\nLosses: `{stats['chess_bullet']['record']['loss']}`\nDraws: `{stats['chess_bullet']['record']['draw']}`",
                    )
                except KeyError:
                    pass

                puzzle_date = stats["tactics"]["highest"]["date"]
                puzzle_date = datetime.fromtimestamp(puzzle_date)
                puzzle_date = puzzle_date.strftime(f"%d.%m.%Y")

                try:
                    # puzzle
                    embed.add_field(
                        name="Puzzle",
                        value=f"Highest: `{stats['tactics']['highest']['rating']}`\nDate: `{puzzle_date}`",
                    )
                except KeyError:
                    pass

                # Send the embed
                await interaction.response.send_message(
                    embed=embed,
                )


@client.tree.command()
@app_commands.describe(
    username="The username of the user you want to get the stats from"
)
async def rapid(interaction: discord.Interaction, username: str):
    """
    Get the rapid stats of a user
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.chess.com/pub/player/{username}/stats"
        ) as resp1:
            if resp1.status == 301 or resp1.status == 404:
                # create embed
                embed = discord.Embed(
                    title="User not found",
                    description="The user you are looking for doesn't exist",
                    color=0xFF0000,
                )
                # send embed
                return await interaction.response.send_message(
                    embed=embed,
                )
            async with session.get(
                f"https://api.chess.com/pub/player/{username}"
            ) as resp2:
                if resp1.status == 429 or resp2.status == 429:
                    # create embed
                    embed = discord.Embed(
                        title="Rate limit exceeded",
                        description="Please try again later",
                        color=0xFF0000,
                    )
                    # send embed
                    return await interaction.response.send_message(
                        embed=embed,
                        ephemeral=True,
                    )

                stats = await resp1.json()
                profile = await resp2.json()

                username = profile["url"].split("/")[-1]

                try:
                    embed = discord.Embed(
                        title=f"{username}'s rapid stats",
                        description=f"**Rating:** `{stats['chess_rapid']['last']['rating']}`\n**Wins:** `{stats['chess_rapid']['record']['win']}`\n**Losses:** `{stats['chess_rapid']['record']['loss']}`\n**Draws:** `{stats['chess_rapid']['record']['draw']}`",
                        color=0x00FF00,
                    )
                except KeyError:
                    # create embed
                    embed = discord.Embed(
                        title="No rapid stats found",
                        description="This user doesn't have any rapid stats",
                        color=0xFF0000,
                    )
                    # send embed
                    return await interaction.response.send_message(
                        embed=embed,
                    )

                # set the thumbnail to the users avatar
                embed.set_thumbnail(url=profile["avatar"])

                try:
                    embed.add_field(
                        name="Highest rating",
                        value=f"`{stats['chess_rapid']['best']['rating']}`",
                        inline=True,
                    )
                except KeyError:
                    pass

                try:
                    embed.add_field(
                        name="Best game",
                        value=f"{stats['chess_rapid']['best']['game']}",
                        inline=True,
                    )
                except KeyError:
                    pass
                # Send the embed
                await interaction.response.send_message(
                    embed=embed,
                )


@client.tree.command()
@app_commands.describe(
    username="The username of the user you want to get the stats from"
)
async def blitz(interaction: discord.Interaction, username: str):
    """
    Get the blitz stats of a user
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.chess.com/pub/player/{username}/stats"
        ) as resp1:
            if resp1.status == 301 or resp1.status == 404:
                # create embed
                embed = discord.Embed(
                    title="User not found",
                    description="The user you are looking for doesn't exist",
                    color=0xFF0000,
                )
                # send embed
                return await interaction.response.send_message(
                    embed=embed,
                )
            async with session.get(
                f"https://api.chess.com/pub/player/{username}"
            ) as resp2:
                if resp1.status == 429 or resp2.status == 429:
                    # create embed
                    embed = discord.Embed(
                        title="Rate limit exceeded",
                        description="Please try again later",
                        color=0xFF0000,
                    )
                    # send embed
                    return await interaction.response.send_message(
                        embed=embed,
                        ephemeral=True,
                    )

                stats = await resp1.json()
                profile = await resp2.json()

                username = profile["url"].split("/")[-1]

                try:
                    embed = discord.Embed(
                        title=f"{username}'s blitz stats",
                        description=f"**Rating:** `{stats['chess_blitz']['last']['rating']}`\n**Wins:** `{stats['chess_blitz']['record']['win']}`\n**Losses:** `{stats['chess_blitz']['record']['loss']}`\n**Draws:** `{stats['chess_blitz']['record']['draw']}`",
                        color=0x00FF00,
                    )
                except KeyError:
                    # create embed
                    embed = discord.Embed(
                        title="No blitz stats found",
                        description="This user doesn't have any blitz stats",
                        color=0xFF0000,
                    )
                    # send embed
                    return await interaction.response.send_message(
                        embed=embed,
                    )

                # set the thumbnail to the users avatar
                embed.set_thumbnail(url=profile["avatar"])

                try:
                    embed.add_field(
                        name="Highest rating",
                        value=f"`{stats['chess_blitz']['best']['rating']}`",
                        inline=True,
                    )
                except KeyError:
                    pass

                try:
                    embed.add_field(
                        name="Best game",
                        value=f"{stats['chess_blitz']['best']['game']}",
                        inline=True,
                    )
                except KeyError:
                    pass
                # Send the embed
                await interaction.response.send_message(
                    embed=embed,
                )


@client.tree.command()
@app_commands.describe(
    username="The username of the user you want to get the stats from"
)
async def bullet(interaction: discord.Interaction, username: str):
    """
    Get the bullet stats of a user
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.chess.com/pub/player/{username}/stats"
        ) as resp1:
            if resp1.status == 301 or resp1.status == 404:
                # create embed
                embed = discord.Embed(
                    title="User not found",
                    description="The user you are looking for doesn't exist",
                    color=0xFF0000,
                )
                # send embed
                return await interaction.response.send_message(
                    embed=embed,
                )
            async with session.get(
                f"https://api.chess.com/pub/player/{username}"
            ) as resp2:
                if resp1.status == 429 or resp2.status == 429:
                    # create embed
                    embed = discord.Embed(
                        title="Rate limit exceeded",
                        description="Please try again later",
                        color=0xFF0000,
                    )
                    # send embed
                    return await interaction.response.send_message(
                        embed=embed,
                        ephemeral=True,
                    )

                stats = await resp1.json()
                profile = await resp2.json()

                username = profile["url"].split("/")[-1]

                try:
                    embed = discord.Embed(
                        title=f"{username}'s bullet stats",
                        description=f"**Rating:** `{stats['chess_bullet']['last']['rating']}`\n**Wins:** `{stats['chess_bullet']['record']['win']}`\n**Losses:** `{stats['chess_bullet']['record']['loss']}`\n**Draws:** `{stats['chess_bullet']['record']['draw']}`",
                        color=0x00FF00,
                    )
                except KeyError:
                    # create embed
                    embed = discord.Embed(
                        title="No bullet stats found",
                        description="This user doesn't have any bullet stats",
                        color=0xFF0000,
                    )
                    # send embed
                    return await interaction.response.send_message(
                        embed=embed,
                    )

                # set the thumbnail to the users avatar
                embed.set_thumbnail(url=profile["avatar"])

                try:
                    embed.add_field(
                        name="Highest rating",
                        value=f"`{stats['chess_bullet']['best']['rating']}`",
                        inline=True,
                    )
                except KeyError:
                    pass

                try:
                    embed.add_field(
                        name="Best game",
                        value=f"{stats['chess_bullet']['best']['game']}",
                        inline=True,
                    )
                except KeyError:
                    pass
                # Send the embed
                await interaction.response.send_message(
                    embed=embed,
                )


@client.tree.command()
@app_commands.describe(
    username="The username of the user you want to get the stats from"
)
async def daily(interaction: discord.Interaction, username: str):
    """
    Get the daily stats of a user
    """

    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.chess.com/pub/player/{username}/stats"
        ) as resp1:
            if resp1.status == 301 or resp1.status == 404:
                # create embed
                embed = discord.Embed(
                    title="User not found",
                    description="The user you are looking for doesn't exist",
                    color=0xFF0000,
                )
                # send embed
                return await interaction.response.send_message(
                    embed=embed,
                )
            async with session.get(
                f"https://api.chess.com/pub/player/{username}"
            ) as resp2:
                if resp1.status == 429 or resp2.status == 429:
                    # create embed
                    embed = discord.Embed(
                        title="Rate limit exceeded",
                        description="Please try again later",
                        color=0xFF0000,
                    )
                    # send embed
                    return await interaction.response.send_message(
                        embed=embed,
                        ephemeral=True,
                    )

                stats = await resp1.json()
                profile = await resp2.json()

                username = profile["url"].split("/")[-1]

                try:
                    embed = discord.Embed(
                        title=f"{username}'s daily stats",
                        description=f"**Rating:** `{stats['chess_daily']['last']['rating']}`\n**Wins:** `{stats['chess_daily']['record']['win']}`\n**Losses:** `{stats['chess_daily']['record']['loss']}`\n**Draws:** `{stats['chess_daily']['record']['draw']}`",
                        color=0x00FF00,
                    )
                except KeyError:
                    # create embed
                    embed = discord.Embed(
                        title="No daily stats found",
                        description="This user doesn't have any daily stats",
                        color=0xFF0000,
                    )
                    # send embed
                    return await interaction.response.send_message(
                        embed=embed,
                    )

                # set the thumbnail to the users avatar
                embed.set_thumbnail(url=profile["avatar"])

                try:
                    embed.add_field(
                        name="Highest rating",
                        value=f"`{stats['chess_daily']['best']['rating']}`",
                        inline=True,
                    )
                except KeyError:
                    pass

                try:
                    embed.add_field(
                        name="Best game",
                        value=f"{stats['chess_daily']['best']['game']}",
                        inline=True,
                    )
                except KeyError:
                    pass
                # Send the embed
                await interaction.response.send_message(
                    embed=embed,
                )


@client.tree.command()
@app_commands.describe(
    username="The username of the user you want to get the stats from"
)
async def puzzle(interaction: discord.Interaction, username: str):
    """
    Get the puzzle stats of a user
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.chess.com/pub/player/{username}/stats"
        ) as resp1:
            if resp1.status == 301 or resp1.status == 404:
                # create embed
                embed = discord.Embed(
                    title="User not found",
                    description="The user you are looking for doesn't exist",
                    color=0xFF0000,
                )
                # send embed
                return await interaction.response.send_message(
                    embed=embed,
                )
            async with session.get(
                f"https://api.chess.com/pub/player/{username}"
            ) as resp2:
                if resp1.status == 429 or resp2.status == 429:
                    # create embed
                    embed = discord.Embed(
                        title="Rate limit exceeded",
                        description="Please try again later",
                        color=0xFF0000,
                    )
                    # send embed
                    return await interaction.response.send_message(
                        embed=embed,
                        ephemeral=True,
                    )

                stats = await resp1.json()
                profile = await resp2.json()

                username = profile["url"].split("/")[-1]

                try:
                    date = stats["tactics"]["highest"]["date"]
                    date = datetime.fromtimestamp(date)
                    date = date.strftime(f"%d.%m.%Y")
                except KeyError:
                    date = "Unknown"

                try:
                    embed = discord.Embed(
                        title=f"{username}'s puzzle stats",
                        description=f"**Highest:** `{stats['tactics']['highest']['rating']}`\n**Date:** `{date}`",
                        color=0x00FF00,
                    )
                except KeyError:
                    # create embed
                    embed = discord.Embed(
                        title="No puzzle stats found",
                        description="This user doesn't have any puzzle stats",
                        color=0xFF0000,
                    )
                    # send embed
                    return await interaction.response.send_message(
                        embed=embed,
                    )

                # set the thumbnail to the users avatar
                embed.set_thumbnail(url=profile["avatar"])

                # Send the embed
                await interaction.response.send_message(
                    embed=embed,
                )


client.run(os.getenv("TOKEN"))
