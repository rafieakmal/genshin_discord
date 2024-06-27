# Imports Don't Remove any!!
import disnake
from disnake.ext import commands, tasks
import os
import subprocess
import platform
import time
import asyncio
import random
import sys
from helpers import errors
import aiohttp
import genshin
import datetime
from database.database import Database
import psutil
import io
import contextlib
import textwrap
import geocoder
import cpuinfo

from requests_and_responses.evening import *
from requests_and_responses.greeting import *
from requests_and_responses.hobby import *
from requests_and_responses.love import *
from requests_and_responses.mean import *
from requests_and_responses.morning import *
from requests_and_responses.night import *
from requests_and_responses.pervy import *
from requests_and_responses.sad import *

# Loading things from config
import config

client_db = Database()

# Setting up the bot
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(config.prefix),
    intents=disnake.Intents.all(),
    case_insensitive=True,
    owner_ids=config.owner_ids
)


async def check_staff_permissions(ctx):
    staff_ids = await client_db.get_staffs_in_server(ctx.guild.id)
    if ctx.author.id not in config.owner_ids and ctx.author.id not in staff_ids:
        embed = disnake.Embed(
            title="Error", description="You are not allowed to use this command!", color=config.Error())
        await ctx.send(embed=embed)
        return False
    return True


@bot.command()
async def whitelistadd(ctx, channel: disnake.TextChannel):
    if not ctx.guild:  # Ensure command is used in a guild
        return await ctx.send("This command can only be used in a server.")
    try:
        if not await check_staff_permissions(ctx):
            return

        channel_id = await client_db.find_one(
            'whitelists', {'channel_id': channel.id})

        # check if the channel is already whitelisted
        if channel_id:
            embed = disnake.Embed(
                title="Error", description="This channel is already whitelisted!", color=config.Error())
            await ctx.send(embed=embed)
            return

        # insert the channel id to mongodb
        await client_db.insert_one(
            'whitelists', {'server_id': ctx.guild.id, 'channel_id': channel.id})
        embed = disnake.Embed(
            title="Success", description=f"Whitelisted the channel {channel.mention}!", color=config.Success())
        await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while whitelisting the user! {e}", color=config.Error())
        await ctx.send(embed=embed)


@bot.command()
async def staffadd(ctx, member: disnake.Member):
    if not ctx.guild:  # Ensure command is used in a guild
        return await ctx.send("This command can only be used in a server.")
    try:
        if ctx.author.id in config.owner_ids:
            # get the channel id from mongodb
            user_id = await client_db.find_one(
                'staffs', {'user_id': member.id})

            # check if the channel is already whitelisted
            if user_id:
                embed = disnake.Embed(
                    title="Error", description="This user is already a staff member!", color=config.Error())
                await ctx.send(embed=embed)
                return

            # insert the channel id to mongodb
            await client_db.insert_one(
                'staffs', {'server_id': ctx.guild.id, 'user_id': member.id})
            embed = disnake.Embed(
                title="Success", description=f"Added {member.mention} as a staff member!", color=config.Success())
            await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(
                title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(
            title="Error", description=f"{e}", color=config.Error())
        await ctx.send(embed=embed)


@bot.command()
async def staffdel(ctx, member: disnake.Member):
    if not ctx.guild:  # Ensure command is used in a guild
        return await ctx.send("This command can only be used in a server.")
    try:
        if ctx.author.id in config.owner_ids:
            # check if the user is a staff member
            user_id = await client_db.find_one('staffs', {'user_id': member.id})
            if not user_id:
                embed = disnake.Embed(
                    title="Error", description="This user is not a staff member!", color=config.Error())
                await ctx.send(embed=embed)
                return

            # delete the user from staffs collection
            await client_db.delete_one('staffs', {'user_id': member.id})
            embed = disnake.Embed(
                title="Success", description=f"Removed {member.mention} from staff members!", color=config.Success())
            await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(
                title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(
            title="Error", description=f"{e}", color=config.Error())
        await ctx.send(embed=embed)


@bot.command()
async def denylistadd(ctx, channel: disnake.TextChannel):
    if not ctx.guild:  # Ensure command is used in a guild
        return await ctx.send("This command can only be used in a server.")
    try:
        if not await check_staff_permissions(ctx):
            return

        # get the channel id from mongodb
        channel_id = await client_db.find_one(
            'blacklists', {'channel_id': channel.id})

        # check if the channel is already blacklisted
        if not channel_id:
            embed = disnake.Embed(
                title="Error", description="This channel is not whitelisted!", color=config.Error())
            await ctx.send(embed=embed)
            return

        # delete the channel id from mongodb
        await client_db.delete_one('whitelists', {'channel_id': channel.id})
        embed = disnake.Embed(
            title="Success", description=f"Denylisted the channel {channel.mention}!", color=config.Success())
        await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while denylisting the channel! {e}", color=config.Error())
        await ctx.send(embed=embed)


@bot.command()
async def whitelistdel(ctx, channel: disnake.TextChannel):
    if not ctx.guild:  # Ensure command is used in a guild
        return await ctx.send("This command can only be used in a server.")
    try:
        if not await check_staff_permissions(ctx):
            return

        # get the channel id from mongodb
        channel_id = await client_db.find_one(
            'whitelists', {'channel_id': channel.id})

        # check if the channel is already whitelisted
        if not channel_id:
            embed = disnake.Embed(
                title="Error", description="This channel is not whitelisted!", color=config.Error())
            await ctx.send(embed=embed)
            return

        # delete the channel id from mongodb
        await client_db.delete_one('whitelists', {'channel_id': channel.id})
        embed = disnake.Embed(
            title="Success", description=f"Removed the channel {channel.mention} from the whitelist!", color=config.Success())
        await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while removing the channel from the whitelist! {e}", color=config.Error())
        await ctx.send(embed=embed)


@bot.command()
async def denylistdel(ctx, channel: disnake.TextChannel):
    if not ctx.guild:  # Ensure command is used in a guild
        return await ctx.send("This command can only be used in a server.")
    try:
        if not await check_staff_permissions(ctx):
            return

        # get the channel id from mongodb
        channel_id = await client_db.find_one(
            'blacklists', {'channel_id': channel.id})

        # check if the channel is already blacklisted
        if not channel_id:
            embed = disnake.Embed(
                title="Error", description="This channel is not blacklisted!", color=config.Error())
            await ctx.send(embed=embed)
            return

        # delete the channel id from mongodb
        await client_db.delete_one('blacklists', {'channel_id': channel.id})
        embed = disnake.Embed(
            title="Success", description=f"Removed the channel {channel.mention} from the blacklist!", color=config.Success())
        await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while removing the channel from the blacklist! {e}", color=config.Error())
        await ctx.send(embed=embed)


@bot.command()
async def restrictmode(ctx, status: str):
    try:
        if ctx.author.id in config.owner_ids:
            if status.lower() == "on":
                await client_db.insert_one('restrictmode', {'server_id': ctx.guild.id, 'status': 'on'})
                embed = disnake.Embed(
                    title="Success", description="Restricted mode is now enabled!", color=config.Success())
                await ctx.send(embed=embed)
            elif status.lower() == "off":
                await client_db.update_one('restrictmode', {'server_id': ctx.guild.id}, {'$set': {'status': 'off'}})
                embed = disnake.Embed(
                    title="Success", description="Restricted mode is now disabled!", color=config.Success())
                await ctx.send(embed=embed)
            else:
                embed = disnake.Embed(
                    title="Error", description="Please provide a valid status! (on/off)", color=config.Error())
                await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(
                title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while changing the restrict mode! {e}", color=config.Error())
        await ctx.send(embed=embed)


@bot.command()
async def update(ctx):
    if not ctx.guild:  # Check if the command is used in a server
        return await ctx.send("This command can only be used in a server.")
    try:
        if ctx.author.id in config.owner_ids:
            if platform.system() == "Windows":
                try:
                    embed = disnake.Embed(
                        title="Updating... (Windows)", description="Updating the bot from the Github Repo...", color=config.Success())
                    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=config.icon_url_front)
                    await ctx.send(embed=embed)
                    subprocess.call('cls')
                    subprocess.call("git pull", shell=True)
                    subprocess.call([sys.executable, "main.py"])
                    sys.exit()
                except Exception as e:
                    await ctx.send("Git failed to update the bot! Please try again later. Error: " + str(e))

            elif platform.system() == "Linux":
                try:
                    embed = disnake.Embed(
                        title="Updating... (Linux)", description="Updating the bot from the Github Repo...", color=config.Success())
                    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=config.icon_url_front)
                    await ctx.send(embed=embed)
                    subprocess.call('clear')
                    subprocess.call(["git", "pull"])
                    subprocess.call([sys.executable, "main.py"])
                    sys.exit()
                except Exception as e:
                    await ctx.send("Git failed to update the bot! Please try again later. Error: " + str(e))
            else:
                embed = disnake.Embed(
                    title="Error", description="Your OS is not supported!", color=config.Error())
                await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(
                title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while updating the bot! {e}", color=config.Error())
        await ctx.send(embed=embed)


@bot.command()
async def getwhitelist(ctx):
    if not ctx.guild:  # Check if the command is used in a server
        return await ctx.send("This command can only be used in a server.")
    try:
        if not await check_staff_permissions(ctx):
            return

        whitelist = await client_db.find(
            'whitelists', {'server_id': ctx.guild.id})
        if whitelist:
            # tag the channel
            channels = []
            no = 1
            for channel in whitelist:
                channels.append(f"{no}. <#{channel['channel_id']}>")
                no += 1
            embed = disnake.Embed(title="Whitelisted Channels", description="\n".join(
                channels), color=config.Success())
            await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(
                title="Error", description="No channels are whitelisted!", color=config.Error())
            await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while fetching the whitelist! {e}", color=config.Error())
        await ctx.send(embed=embed)


@bot.command()
async def getclaimedusers(ctx):
    if not ctx.guild:  # Check if the command is used in a server
        return await ctx.send("This command can only be used in a server.")
    try:
        if not await check_staff_permissions(ctx):
            return

        users = await client_db.find(
            'users_claimed', {'server_id': ctx.guild.id})
        if users:
            # tag the user
            user_list = []
            no = 1
            for user in users:
                user_list.append(
                    f"{no}. <@{user['user_id']}> - UID: {user['uid']}")
                no += 1
            embed = disnake.Embed(title="Claimed Users", description="\n".join(
                user_list), color=config.Success())
            await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(
                title="Error", description="No users have claimed the Abyss Master role!", color=config.Error())
            users = await client_db.find(
                'users_claimed', {'server_id': ctx.guild.id})
            if users:
                # tag the user
                user_list = []
                no = 1
                for user in users:
                    user_list.append(
                        f"{no}. <@{user['user_id']}> - UID: {user['uid']}")
                    no += 1
                embed = disnake.Embed(title="Claimed Users", description="\n".join(
                    user_list), color=config.Success())
                await ctx.send(embed=embed)
            else:
                embed = disnake.Embed(
                    title="Error", description="No users have claimed the Abyss Master role!", color=config.Error())
                await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while fetching the claimed users! {e}", color=config.Error())
        await ctx.send(embed=embed)


@bot.command()
async def getabyssmaster(ctx):
    if not ctx.guild:  # Check if the command is used in a server
        return await ctx.send("This command can only be used in a server.")
    try:
        staff_ids = await client_db.get_staffs_in_server(ctx.guild.id)

        if ctx.author.id not in config.owner_ids and ctx.author.id not in staff_ids:
            embed = disnake.Embed(
                title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
        else:
            guild = ctx.guild
            role = disnake.utils.get(guild.roles, name='Abyss Master')

            if role:
                member_ids = [
                    member.id for member in guild.members if member.roles and role in member.roles]

                # tag the user
                user_list = []

                if member_ids:
                    no = 1
                    for member_id in member_ids:
                        user = guild.get_member(member_id)
                        user_list.append(f"{no}. {user.mention}")
                        no += 1
                    embed = disnake.Embed(title="Abyss Master Role", description="\n".join(
                        user_list), color=config.Success())
                    await ctx.send(embed=embed)
                else:
                    embed = disnake.Embed(
                        title="Error", description="No users have Abyss Master role!", color=config.Error())
                    await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while fetching the claimed users! {e}", color=config.Error())
        await ctx.send(embed=embed)


@bot.command()
async def resetabyssdata(ctx, uid=None):
    if not ctx.guild:  # Check if the command is used in a server
        return await ctx.send("This command can only be used in a server.")
    try:
        staff_ids = await client_db.get_staffs_in_server(ctx.guild.id)

        if ctx.author.id not in config.owner_ids and ctx.author.id not in staff_ids:
            embed = disnake.Embed(
                title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
        else:
            if uid != None:
                # check uid length must be between 9 and 10
                if len(uid) < 9 or len(uid) > 10:
                    return await ctx.send("Please provide a valid user id")

                # check if uid is a number
                if not uid.isdigit():
                    return await ctx.send("Please provide a valid user id")

                # check if uid registered in the database
                user = await client_db.find_one('users_claimed', {'uid': uid})
                if user:
                    await client_db.delete_one('users_claimed', {'uid': uid})
                    return await ctx.send(f"Deleted the Abyss Master role for user with id: {uid}")
                else:
                    return await ctx.send(f"User with id: {uid} has not claimed the Abyss Master role")
            else:
                # delete all users from the database with server id
                await client_db.delete_many('users_claimed', {'server_id': ctx.guild.id})
                return await ctx.send("Deleted all Abyss Master roles")
    except Exception as e:
        await ctx.send(embed=errors.create_error_embed(f"{e}"))


@bot.command()
async def resetabyssrole(ctx, member: disnake.Member):
    if not ctx.guild:  # Check if the command is used in a server
        return await ctx.send("This command can only be used in a server.")

    try:
        staff_ids = await client_db.get_staffs_in_server(ctx.guild.id)

        if ctx.author.id not in config.owner_ids and ctx.author.id not in staff_ids:
            embed = disnake.Embed(
                title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
        else:
            if member:
                role = disnake.utils.get(ctx.guild.roles, name='Abyss Master')
                if role:
                    await member.remove_roles(role)
                    return await ctx.send(f"Removed the Abyss Master role from {member.mention}")
                else:
                    embed = disnake.Embed(
                        title="Error", description="Abyss Master role not found!", color=config.Error())
                    await ctx.send(embed=embed)
            else:
                guild = ctx.guild
                role = disnake.utils.get(guild.roles, name='Abyss Master')

                if role:
                    member_ids = [
                        member.id for member in guild.members if member.roles and role in member.roles]

                    if member_ids:
                        # reset all users with Abyss Master role
                        for member_id in member_ids:
                            member = await guild.fetch_member(member_id)
                            await member.remove_roles(role)

                        embed = disnake.Embed(
                            title="Success", description="Removed all Abyss Master roles", color=config.Success())
                        await ctx.send(embed=embed)
                    else:
                        embed = disnake.Embed(
                            title="Error", description="No users have Abyss Master role!", color=config.Error())
                        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=errors.create_error_embed(f"{e}"))


@bot.command()
async def getexploration(ctx, uid):
    try:
        # Check if the command is used in a whitelisted channel or DMs
        channel_id = ctx.channel.id if ctx.channel else ctx.author.id
        whitelisted = await client_db.find_one("whitelists", {"channel_id": channel_id})
        if not whitelisted:
            return await ctx.send("This command is disabled in this channel or DM")

        if not uid or not uid.isdigit() or not (9 <= len(uid) <= 10):
            return await ctx.send("Please provide a valid user id")

        user_logged_in = await client_db.find_one('users', {'user_id': ctx.author.id})
        if not user_logged_in:
            cookies = {"ltuid_v2": config.ltuid_v2,
                       "ltoken_v2": config.ltoken_v2}
        else:
            # Set up Genshin client with user's cookies
            cookies = {key: user_logged_in[key] for key in [
                'ltuid_v2', 'ltoken_v2', 'cookie_token_v2', 'account_id_v2', 'account_mid_v2', 'ltmid_v2']}

        client = genshin.Client(cookies)
        data_profile = await client.get_genshin_user(uid)

        data_exploration = [
            {
                "name": exploration.name,
                "level": exploration.level,
                "exploration_percentage": round((int(exploration.raw_explored) / 1000) * 100, 1),
                "icon": exploration.icon
            } for exploration in data_profile.explorations if exploration.name != "Chenyu Vale"
        ]

        all_data_are_100 = all(
            exploration['exploration_percentage'] == 100 for exploration in data_exploration)
        message_100 = "> Congratulations! All explorations are 100% completed!" if all_data_are_100 else ""

        incomplete_explorations = [exploration['name']
                                   for exploration in data_exploration if exploration['exploration_percentage'] != 100]
        message_100 += "\n> Explorations that are not 100% completed:\n" + \
            "\n".join([f"> - {name}" for name in incomplete_explorations])

        complete_explorations = [exploration['name']
                                 for exploration in data_exploration if exploration['exploration_percentage'] == 100]
        message_data_100 = "\n> Explorations that are 100% completed:\n" + \
            "\n".join([f"> - {name}" for name in complete_explorations])

        # Assuming this is defined in the config file for better maintainability
        data_emoji_progress = config.data_emoji_progress

        embed = disnake.Embed(title=f"{ctx.author.name}'s Exploration Progress",
                              color=config.Success(), timestamp=datetime.datetime.now())
        for exploration in data_exploration:
            progress_emoji = get_progress_emoji(
                exploration['exploration_percentage'], data_emoji_progress)
            embed.add_field(
                name=f"{config.block_star_emoji} {exploration['name']} - <:world_level:1225721002588114954> {exploration['level']}",
                value=f"\n> Progress: {exploration['exploration_percentage']}%\n> {progress_emoji}",
                inline=False
            )

        embed.add_field(name=f"{config.block_star_emoji} Note",
                        value=message_100, inline=False)
        embed.add_field(name=f"{config.block_star_emoji} Extra Note",
                        value=message_data_100, inline=False)
        embed.set_footer(text=f"Requested by {ctx.author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
        embed.set_image(url=config.banner_exploration)

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=errors.create_error_embed(f"{e}"))


def get_progress_emoji(percentage, emoji_dict):
    """Returns the appropriate progress bar emoji based on the exploration percentage."""
    if percentage == 100:
        return f"<:start_full:{emoji_dict['start_full']}>" + (f"<:mid_full:{emoji_dict['mid_full']}>" * 4) + f"<:back_full:{emoji_dict['back_full']}>"
    elif 60 <= percentage < 100:
        return f"<:start_full:{emoji_dict['start_full']}>" + (f"<:mid_full:{emoji_dict['mid_full']}>" * 4) + f"<:back_blank:{emoji_dict['back_blank']}>"
    elif 30 <= percentage < 60:
        return f"<:start_full:{emoji_dict['start_full']}><:mid_full:{emoji_dict['mid_full']}>" + (f"<:mid_blank:{emoji_dict['mid_blank']}>" * 3) + f"<:back_blank:{emoji_dict['back_blank']}>"
    elif 10 <= percentage < 30:
        return f"<:start_full:{emoji_dict['start_full']}>" + (f"<:mid_blank:{emoji_dict['mid_blank']}>" * 4) + f"<:back_blank:{emoji_dict['back_blank']}>"
    else:
        return f"<:start_blank:{emoji_dict['start_blank']}>" + (f"<:mid_blank:{emoji_dict['mid_blank']}>" * 4) + f"<:back_blank:{emoji_dict['back_blank']}>"


@bot.command()
async def setprefix(ctx, prefix):
    try:
        if ctx.author.id in config.owner_ids:
            # change the prefix from config
            config.prefix = prefix

            # send the success message
            embed = disnake.Embed(title="Success", description=f"Prefix changed to {prefix}", color=config.Success())
            await ctx.send(embed=embed)
        else:
            await ctx.send("You are not allowed to use this command!")
    except Exception as e:
        await ctx.send(embed=errors.create_error_embed(f"{e}"))


@bot.command()
async def menu(ctx):
    try:
        # if current server is restricted
        restricted = await client_db.find_one('restrictmode', {'server_id': ctx.guild.id})
        if restricted and restricted['status'] == 'on':
            # check channel is whitelisted
            whitelist = await client_db.find_one('whitelists', {'channel_id': ctx.channel.id})
            if not whitelist:
                return

            embedVar = disnake.Embed(
                title="General Commands!",
                description="Check important commands, that you can use!",
                colour=config.Success())
            embedVar.add_field(name="General Commands",
                               value=f"```{config.prefix}reqabyssmaster uid - To request role Abyss Master```\n```{config.prefix}getexploration uid - To get the exploration stats```\n",
                               inline=False)
            embedVar.set_footer(text=f"Requested by {ctx.author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
            embedVar.set_image(
                url=config.banner_success
            )
            await ctx.send(embed=embedVar)
        else:
            # check channel is whitelisted
            whitelist = await client_db.find_one('whitelists', {'channel_id': ctx.channel.id})
            if not whitelist:
                return

            embedVar = disnake.Embed(
                title="General Commands!",
                description="Check important commands, that you can use!",
                colour=config.Success())
            embedVar.add_field(name="General Commands", value=f"```{config.prefix}reqabyssmaster uid - To request role Abyss Master``````{config.prefix}getexploration uid - To get the exploration stats```\n",inline=False)
            embedVar.set_footer(text=f"Requested by {ctx.author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
            embedVar.set_image(
                url=config.banner_success
            )
            await ctx.send(embed=embedVar)
    except Exception as e:
        await ctx.send(embed=errors.create_error_embed(f"{e}"))


@bot.command()
async def ping(ctx):
    try:
        message = f"Websocket's latency: {round(bot.latency * 1000)}ms"
        message += f"\nWebsocket's rate limited: {bot.is_ws_ratelimited()}"
        embed = disnake.Embed(
            title=f"PONG!", description=message, color=config.Success())
        embed.set_footer(
            text=f'Command executed by {ctx.author}', icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=errors.create_error_embed(f"Error sending ping command: {e}"))


@bot.command()
async def system(ctx):
    try:
        uname = platform.uname()
        processor = cpuinfo.get_cpu_info()['brand_raw']
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        memory_info = psutil.Process().memory_full_info()
        physical_memory_used = memory_info.rss / (1024 ** 2)
        virtual_memory_used = memory_info.vms / (1024 ** 2)
        pid = os.getpid()
        process = psutil.Process(pid)
        threads = process.num_threads()

        total_ram = psutil.virtual_memory().total / (1024 ** 3)  # Convert bytes to GB
        used_ram = psutil.virtual_memory().used / (1024 ** 3)  # Convert bytes to GB
        g = geocoder.ip('me')
        system_info = f"System: {uname.system}\n"
        system_info += f"Node Name: {uname.node}\n"
        system_info += f"Release: {uname.release}\n"
        system_info += f"Version: {uname.version}\n"
        system_info += f"Machine: {uname.machine}\n"
        system_info += f"Processor: {processor}\n"
        system_info += f"CPU Usage: {cpu_usage}%\n"
        system_info += f"RAM Usage: {ram_usage}%\n"
        system_info += f"Total RAM: {used_ram:.2f} GB/{total_ram:.2f} GB\n"
        system_info += f"Location: {g.country}, {g.city}\n"
        system_info += f"Using {physical_memory_used:.2f} MiB physical memory and {virtual_memory_used:.2f} MiB virtual memory.\n"
        system_info += f"Running on PID {pid} with {threads} thread(s)."

        embed = disnake.Embed(
            title="System", description=f"```{system_info}```", color=config.Success())
        embed.set_footer(
            text=f'Command executed by {ctx.author}', icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=errors.create_error_embed(f"{e}"))


@bot.command()
async def execute(ctx, *, message: str):
    if ctx.author.id not in config.owner_ids:
        return await ctx.send("You don't have permission to use this command.")

    env = {
        'bot': bot,
        'ctx': ctx,
        'disnake': disnake,
        'config': config,
        'client_db': client_db,
        'errors': errors,
        'platform': platform,
        'psutil': psutil,
        'os': os,
    }

    try:
        # Execute the code within the restricted environment
        with io.StringIO() as buf:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                exec(message, env, env)
                output = buf.getvalue()

        if output:
            await ctx.send(f"```{output}```")
        else:
            await ctx.send("Executed without output.")
    except Exception as e:
        await ctx.send(embed=errors.create_error_embed(f"{e}"))


@bot.command()
async def say(ctx, channel: disnake.TextChannel, *, message: str):
    if not ctx.guild:  # Ensure command is used in a server
        return await ctx.send("This command can only be used in a server.")
    try:
        # get current staff ids in a server
        staff_ids = await client_db.get_staffs_in_server(ctx.guild.id)

        if ctx.author.id not in config.owner_ids and ctx.author.id not in staff_ids:
            return await ctx.send("You don't have permission to use this command")
        await channel.send(message)
        await ctx.send(content=f"Message sent to {channel.mention}")
    except Exception as e:
        await ctx.send(embed=errors.create_error_embed(f"{e}"))


@bot.command()
async def reply(ctx, channel: disnake.TextChannel, message_id: str, *, message: str):
    if not ctx.guild:  # Ensure command is used in a server
        return await ctx.send("This command can only be used in a server.")
    try:
        staff_ids = await client_db.get_staffs_in_server(ctx.guild.id)

        if ctx.author.id not in config.owner_ids and ctx.author.id not in staff_ids:
            return await ctx.send("You don't have permission to use this command")
        message_to_reply = await channel.fetch_message(message_id)
        if not message_to_reply:
            return await ctx.send("Message not found.")
        await message_to_reply.reply(message)
        await ctx.send(content=f"Replied to the message in {channel.mention}")
    except Exception as e:
        await ctx.send(embed=errors.create_error_embed(f"Error replying to message: {e}"))


@bot.command()
async def reqabyssmaster(ctx, uid: str):
    try:
        # Check if the channel is whitelisted
        channel_id = ctx.channel.id if ctx.channel else False
        whitelisted = await client_db.find_one("whitelists", {"channel_id": channel_id})
        if not whitelisted:
            return await ctx.send("This command is disabled in this channel or DM")

        # Validate UID input
        if not uid or not uid.isdigit() or not (9 <= len(uid) <= 10):
            return await ctx.send("Please provide a valid user id")

        # Check if the user has already claimed the Abyss Master role
        user = await client_db.find_one('users_claimed', {'uid': uid, 'server_id': ctx.guild.id})
        if user:
            return await ctx.send("This user has already claimed the Abyss Master role")

        # Fetch user's Spiral Abyss data
        user_logged_in = await client_db.find_one('users', {'user_id': ctx.author.id})

        if not user_logged_in:
            cookies = {"ltuid_v2": config.ltuid_v2,
                       "ltoken_v2": config.ltoken_v2}
        else:
            # Set up Genshin client with user's cookies
            cookies = {key: user_logged_in[key] for key in [
                'ltuid_v2', 'ltoken_v2', 'cookie_token_v2', 'account_id_v2', 'account_mid_v2', 'ltmid_v2']}

        client = genshin.Client(cookies)
        data_abyss = await client.get_spiral_abyss(uid, previous=False)

        # Fetch user's general game info
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://enka.network/api/uid/{uid}") as response:
                if response.status != 200:
                    return await ctx.send("Error: Unable to fetch user info")

                data = await response.json()
                player_info = data.get('playerInfo', {})
                nickname = player_info.get('nickname', 'None')
                level = player_info.get('level', 'None')
                world_level = player_info.get('worldLevel', 'None')
                tower_floor_index = player_info.get('towerFloorIndex', 'None')
                tower_level_index = player_info.get('towerLevelIndex', 'None')
                total_stars = data_abyss.total_stars

                # Check if the user meets the criteria for the Abyss Master role
                if int(tower_floor_index) != 12 or int(tower_level_index) != 3 or int(total_stars) < 36:
                    message = "> You do not meet the criteria for the Abyss Master role."
                    embed_color = config.Error()
                    banner_url = config.banner_error
                else:
                    # Grant the Abyss Master role
                    role = disnake.utils.get(
                        ctx.guild.roles, name='Abyss Master')
                    if role:
                        member = ctx.guild.get_member(ctx.author.id)
                        await member.add_roles(role)
                        await client_db.insert_one('users_claimed', {'uid': uid, 'user_id': ctx.author.id, 'server_id': ctx.guild.id})
                        message = "> Congratulations! You have been granted the Abyss Master role."
                        embed_color = config.Success()
                        banner_url = config.banner_success
                    else:
                        message = "> Abyss Master role not found."
                        embed_color = config.Error()
                        banner_url = config.banner_error

                # Construct and send the response embed
                embedVar = disnake.Embed(
                    title=f"{nickname}'s Abyss Info",
                    color=embed_color,
                    timestamp=datetime.datetime.now())
                embedVar.add_field(name="<:block_star:1225801267893370961> Adventure Rank", value=f"> {level}", inline=False)
                embedVar.add_field(name="<:block_star:1225801267893370961> World Level", value=f"> {world_level}", inline=False)
                embedVar.add_field(name="<:block_star:1225801267893370961> Abyss Progress", value=f"> Floor {tower_floor_index} - Chamber {tower_level_index}", inline=False)
                embedVar.add_field(name="<:block_star:1225801267893370961> Abyss Stars Collected", value=f"> {total_stars} <:abyss_stars:1225579783660765195>", inline=False)
                embedVar.add_field(
                    name="<:block_star:1225801267893370961> Note", value=message, inline=False)
                embedVar.set_footer(text=f"Requested by {ctx.author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
                embedVar.set_image(url=banner_url)

                await ctx.send(embed=embedVar)

    except Exception as e:
        # handle retcode 10102 (User's data is not public)
        if e.retcode == 10102:
            await handle_user_not_public(ctx)
        else:
            await ctx.send(embed=errors.create_error_embed(f"{e}"))


async def handle_user_not_public(ctx):
    embedVar = disnake.Embed(
        title="User's data is not public",
        color=config.Error(),
        timestamp=datetime.datetime.now()
    )
    embedVar.add_field(name="How to make your data public?",
                       value="> Go to privacy settings -> scroll down and turn on Show my Battle Chronicle on my profile", inline=False)
    embedVar.set_footer(text=f"Requested by {ctx.author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
    embedVar.set_image(url="https://i.ibb.co/1nmyXZ7/ezgif-6-1cafb9783e.gif")
    await ctx.send(embed=embedVar)

# On Ready


@bot.event
async def on_ready():
    print("The bot is ready!")
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator} | {bot.user.id}')
    print(f"I am on {len(bot.guilds)} server")
    print(f'Running on {platform.system()} {platform.release()} ({os.name})')
    print(f'Bot Version: {config.version}')
    print(f"disnake version : {disnake.__version__}")
    print(f"Python version: {platform.python_version()}")
    status_task.start()


@bot.event
async def on_message(message):
    # Make sure the bot doesn't reply to itself
    if message.author == bot.user:
        return

    msg = message.content.lower()

    try:
        if any(msg == phrase for phrase in greeting_requests):
            await message.channel.send(random.choice(greeting_responses))

        elif any(msg == phrase for phrase in morning_requests):
            await message.channel.send(random.choice(morning_responses))

        elif any(msg == phrase for phrase in evening_requests):
            await message.channel.send(random.choice(evening_responses))

        elif any(msg == phrase for phrase in love_requests):
            await message.channel.send(random.choice(love_responses))

        elif any(msg == phrase for phrase in pervy_requests):
            await message.channel.send(random.choice(pervy_responses))

        elif any(msg == phrase for phrase in social_greeting):
            await message.channel.send(random.choice(social_greeting_replies))

        elif any(msg == phrase for phrase in sad_requests):
            await message.channel.send(random.choice(encouraging_responses))

        elif any(msg == phrase for phrase in mean_requests):
            await message.channel.send(random.choice(mean_responses))

        elif any(msg == phrase for phrase in hobby_requests):
            await message.channel.send(random.choice(hobby_responses))
    except disnake.errors.Forbidden:
        print("Bot does not have permission to send messages in this channel.")
    else:
        await bot.process_commands(message)


# Status Task
@tasks.loop(minutes=0.15)
async def status_task():
    await bot.change_presence(activity=disnake.Game(random.choice(config.activity)))

# Load Cogs On Start
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

# Run The Bot
bot.run(config.token, reconnect=True)