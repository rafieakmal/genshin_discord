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

@bot.command()
async def whitelistadd(ctx, channel: disnake.TextChannel):
    try:
        staff_ids = await client_db.get_staffs_in_server(ctx.guild.id)

        if ctx.author.id not in config.owner_ids and ctx.author.id not in staff_ids:
            embed = disnake.Embed(
                title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
            
        channel_id = client_db.find_one(
            'whitelists', {'channel_id': channel.id})

        # check if the channel is already whitelisted
        if channel_id:
            embed = disnake.Embed(
                title="Error", description="This channel is already whitelisted!", color=config.Error())
            await ctx.send(embed=embed)
            return

        # insert the channel id to mongodb
        client_db.insert_one(
            'whitelists', {'server_id': ctx.guild.id, 'channel_id': channel.id})
        embed = disnake.Embed(
            title="Success", description=f"Whitelisted the channel {channel.mention}!", color=config.Success())
        await ctx.send(embed=embed)            
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while whitelisting the user! {e}", color=config.Error())
        await ctx.send(embed=embed)


@bot.command()
async def staffadd(ctx, member: disnake.Member):
    try:
        if ctx.author.id in config.owner_ids:
            # get the channel id from mongodb
            user_id = client_db.find_one(
                'staffs', {'user_id': member.id})

            # check if the channel is already whitelisted
            if user_id:
                embed = disnake.Embed(
                    title="Error", description="This user is already a staff member!", color=config.Error())
                await ctx.send(embed=embed)
                return

            # insert the channel id to mongodb
            client_db.insert_one(
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
    try:
        if ctx.author.id in config.owner_ids:
            # check if the user is a staff member
            user_id = client_db.find_one('staffs', {'user_id': member.id})
            if not user_id:
                embed = disnake.Embed(
                    title="Error", description="This user is not a staff member!", color=config.Error())
                await ctx.send(embed=embed)
                return

            # delete the user from staffs collection
            client_db.delete_one('staffs', {'user_id': member.id})
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
    try:
        staff_ids = await client_db.get_staffs_in_server(ctx.guild.id)

        if ctx.author.id not in config.owner_ids and ctx.author.id not in staff_ids:
            embed = disnake.Embed(title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
        
        # get the channel id from mongodb
        channel_id = client_db.find_one(
            'blacklists', {'channel_id': channel.id})

        # check if the channel is already blacklisted
        if not channel_id:
            embed = disnake.Embed(
                title="Error", description="This channel is not whitelisted!", color=config.Error())
            await ctx.send(embed=embed)
            return

        # delete the channel id from mongodb
        client_db.delete_one('whitelists', {'channel_id': channel.id})
        embed = disnake.Embed(
            title="Success", description=f"Denylisted the channel {channel.mention}!", color=config.Success())
        await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while denylisting the channel! {e}", color=config.Error())
        await ctx.send(embed=embed)

@bot.command()
async def whitelistdel(ctx, channel: disnake.TextChannel):
    try:
        staff_ids = await client_db.get_staffs_in_server(ctx.guild.id)

        if ctx.author.id not in config.owner_ids and ctx.author.id not in staff_ids:
            embed = disnake.Embed(
                title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
        
        # get the channel id from mongodb
        channel_id = client_db.find_one(
            'whitelists', {'channel_id': channel.id})

        # check if the channel is already whitelisted
        if not channel_id:
            embed = disnake.Embed(
                title="Error", description="This channel is not whitelisted!", color=config.Error())
            await ctx.send(embed=embed)
            return

        # delete the channel id from mongodb
        client_db.delete_one('whitelists', {'channel_id': channel.id})
        embed = disnake.Embed(
            title="Success", description=f"Removed the channel {channel.mention} from the whitelist!", color=config.Success())
        await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while removing the channel from the whitelist! {e}", color=config.Error())
        await ctx.send(embed=embed)

@bot.command()
async def denylistdel(ctx, channel: disnake.TextChannel):
    try:
        staff_ids = await client_db.get_staffs_in_server(ctx.guild.id)

        if ctx.author.id not in config.owner_ids and ctx.author.id not in staff_ids:
            embed = disnake.Embed(title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)

        # get the channel id from mongodb
        channel_id = client_db.find_one(
            'blacklists', {'channel_id': channel.id})

        # check if the channel is already blacklisted
        if not channel_id:
            embed = disnake.Embed(
                title="Error", description="This channel is not blacklisted!", color=config.Error())
            await ctx.send(embed=embed)
            return

        # delete the channel id from mongodb
        client_db.delete_one('blacklists', {'channel_id': channel.id})
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
                client_db.insert_one('restrictmode', {'server_id': ctx.guild.id, 'status': 'on'})
                embed = disnake.Embed(title="Success", description="Restricted mode is now enabled!", color=config.Success())
                await ctx.send(embed=embed)
            elif status.lower() == "off":
                client_db.update_one('restrictmode', {'server_id': ctx.guild.id}, {'$set': {'status': 'off'}})
                embed = disnake.Embed(title="Success", description="Restricted mode is now disabled!", color=config.Success())
                await ctx.send(embed=embed)
            else:
                embed = disnake.Embed(title="Error", description="Please provide a valid status! (on/off)", color=config.Error())
                await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while changing the restrict mode! {e}", color=config.Error())
        await ctx.send(embed=embed)

@bot.command()
async def update(ctx):
    try:
        if ctx.author.id in config.owner_ids:
            if platform.system() == "Windows":
                try:
                    embed = disnake.Embed(title="Updating... (Windows)", description="Updating the bot from the Github Repo...", color=config.Success())
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
                    embed = disnake.Embed(title="Updating... (Linux)", description="Updating the bot from the Github Repo...", color=config.Success())
                    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=config.icon_url_front)
                    await ctx.send(embed=embed)
                    subprocess.call('clear')
                    subprocess.call(["git", "pull"])
                    subprocess.call([sys.executable, "main.py"])
                    sys.exit()
                except Exception as e:
                    await ctx.send("Git failed to update the bot! Please try again later. Error: " + str(e))
            else:
                embed = disnake.Embed(title="Error", description="Your OS is not supported!", color=config.Error())
                await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while updating the bot! {e}", color=config.Error())
        await ctx.send(embed=embed)

@bot.command()
async def getwhitelist(ctx):
    try:
        staff_ids = await client_db.get_staffs_in_server(ctx.guild.id)

        if ctx.author.id not in config.owner_ids and ctx.author.id not in staff_ids:
            embed = disnake.Embed(
                title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
        else:
            whitelist = client_db.find(
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
    try:
        staff_ids = await client_db.get_staffs_in_server(ctx.guild.id)

        if ctx.author.id not in config.owner_ids and ctx.author.id not in staff_ids:
            embed = disnake.Embed(
                title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
        else:
            users = client_db.find(
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
async def resetabyssdata(ctx, uid = None):
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
                user = client_db.find_one('users_claimed', {'uid': uid})
                if user:
                    client_db.delete_one('users_claimed', {'uid': uid})
                    return await ctx.send(f"Deleted the Abyss Master role for user with id: {uid}")
                else:
                    return await ctx.send(f"User with id: {uid} has not claimed the Abyss Master role")
            else:
                # delete all users from the database with server id
                client_db.delete_many('users_claimed', {'server_id': ctx.guild.id})
                return await ctx.send("Deleted all Abyss Master roles")
    except Exception as e:
        (f'Error sending help message: {e}')
        await ctx.send(embed=errors.create_error_embed(f"{e}"))
        

@bot.command()
async def resetabyssrole(ctx, member: disnake.Member):
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
                    embed = disnake.Embed(title="Error", description="Abyss Master role not found!", color=config.Error())
                    await ctx.send(embed=embed)
            else:
                guild = ctx.guild
                role = disnake.utils.get(guild.roles, name='Abyss Master')

                if role:
                    member_ids = [member.id for member in guild.members if member.roles and role in member.roles]
                    
                    if member_ids:
                        # reset all users with Abyss Master role
                        for member_id in member_ids:
                            member = await guild.fetch_member(member_id)
                            await member.remove_roles(role)
                        
                        embed = disnake.Embed(title="Success", description="Removed all Abyss Master roles", color=config.Success())
                        await ctx.send(embed=embed)
                    else:
                        embed = disnake.Embed(title="Error", description="No users have Abyss Master role!", color=config.Error())
                        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=errors.create_error_embed(f"{e}"))

@bot.command()
async def getexploration(ctx, uid):
    try:
            if uid == None or uid == "":
                return await ctx.send("Please provide a user id")
                    
            # check uid length must be between 9 and 10
            if len(uid) < 9 or len(uid) > 10:
                return await ctx.send("Please provide a valid user id")
                
                # check if uid is a number
            if not uid.isdigit():
                return await ctx.send("Please provide a valid user id")

            cookies = {"ltuid_v2": config.ltuid_v2, "ltoken_v2": config.ltoken_v2}
            client = genshin.Client(cookies)
                    
            data_profile = await client.get_genshin_user(uid)

            data_exploration = []

            for exploration in data_profile.explorations:
                if exploration.name == "Chenyu Vale":
                    continue

                data_exploration.append({
                    "name": exploration.name,
                    "level": exploration.level,
                    "exploration_percentage": round((int(exploration.raw_explored) / 1000) * 100, 1),
                    "icon": exploration.icon
                })

            all_data_are_100 = all(exploration['exploration_percentage'] == 100 for exploration in data_exploration)

            message_100 = ""
            if all_data_are_100:
                message_100 += "> Congratulations! All explorations are 100% completed!"
            else:
                all_data_are_not_100 = [exploration['name'] for exploration in data_exploration if exploration['exploration_percentage'] != 100]

                message_100 += "> Explorations that are not 100% completed:"
                for exploration in all_data_are_not_100:
                    message_100 += f"\n> - {exploration}"
                
                message_data_100 = "> Explorations that are 100% completed:"
                data_that_are_100 = [exploration['name'] for exploration in data_exploration if exploration['exploration_percentage'] == 100]
                for exploration in data_that_are_100:
                    message_data_100 += f"\n> - {exploration}"
                

            data_emoji_progress = {
                "start_blank": 1225706893960282184,
                "start_full": 1225706895915094067,
                "mid_blank": 1225706884611444787,
                "mid_full": 1225706891196502047,
                "back_blank": 1225706887366971443,
                "back_full": 1225706888939962399
            }

            author = ctx.author
            embed = disnake.Embed(title=f"{author.name}'s Exploration Progress", color=config.Success(), timestamp=datetime.datetime.now())

            for exploration in data_exploration:
                message = ""

                if exploration['exploration_percentage'] == 100:
                    message += f"\n> Progress: {exploration['exploration_percentage']}%\n> <:start_full:{data_emoji_progress['start_full']}><:mid_full:{data_emoji_progress['mid_full']}><:mid_full:{data_emoji_progress['mid_full']}><:mid_full:{data_emoji_progress['mid_full']}><:mid_full:{data_emoji_progress['mid_full']}><:back_full:{data_emoji_progress['back_full']}>"
                elif exploration['exploration_percentage'] >= 60 and exploration['exploration_percentage'] < 100:
                    message += f"\n> Progress: {exploration['exploration_percentage']}%\n> <:start_full:{data_emoji_progress['start_full']}><:mid_full:{data_emoji_progress['mid_full']}><:mid_full:{data_emoji_progress['mid_full']}><:mid_full:{data_emoji_progress['mid_full']}><:mid_full:{data_emoji_progress['mid_full']}><:back_blank:{data_emoji_progress['back_blank']}>"
                elif exploration['exploration_percentage'] >= 30 and exploration['exploration_percentage'] < 60:
                    message += f"\n> Progress: {exploration['exploration_percentage']}%\n> <:start_full:{data_emoji_progress['start_full']}><:mid_full:{data_emoji_progress['mid_full']}><:mid_blank:{data_emoji_progress['mid_blank']}><:mid_blank:{data_emoji_progress['mid_blank']}><:mid_blank:{data_emoji_progress['mid_blank']}><:back_blank:{data_emoji_progress['back_blank']}>"
                elif exploration['exploration_percentage'] >= 10 and exploration['exploration_percentage'] < 30:
                    message += f"\n> Progress: {exploration['exploration_percentage']}%\n> <:start_full:{data_emoji_progress['start_full']}><:mid_blank:{data_emoji_progress['mid_blank']}><:mid_blank:{data_emoji_progress['mid_blank']}><:mid_blank:{data_emoji_progress['mid_blank']}><:mid_blank:{data_emoji_progress['mid_blank']}><:back_blank:{data_emoji_progress['back_blank']}>"
                else:
                    message += f"\n> Progress: {exploration['exploration_percentage']}%\n> <:start_blank:{data_emoji_progress['start_blank']}><:mid_blank:{data_emoji_progress['mid_blank']}><:mid_blank:{data_emoji_progress['mid_blank']}><:mid_blank:{data_emoji_progress['mid_blank']}><:mid_blank:{data_emoji_progress['mid_blank']}><:back_blank:{data_emoji_progress['back_blank']}>"

                embed.add_field(name=f"<:block_star:1225801267893370961> {exploration['name']} - <:world_level:1225721002588114954> {exploration['level']}", value=message, inline=False)
            
            embed.add_field(name="<:block_star:1225801267893370961> Note:", value=message_100, inline=False)
            embed.add_field(name="<:block_star:1225801267893370961> Extra Note:", value=message_data_100, inline=False)
            embed.set_footer(text=f"Requested by {ctx.author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
            embed.set_image(
                url=config.banner_exploration
            )

            await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=errors.create_error_embed(f"{e}"))

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
        restricted = client_db.find_one('restrictmode', {'server_id': ctx.guild.id})
        if restricted and restricted['status'] == 'on':
            # check channel is whitelisted
            whitelist = client_db.find_one('whitelists', {'channel_id': ctx.channel.id})
            if not whitelist:
                return
            
            
            embedVar = disnake.Embed(
                    title="General Commands!",
                    description="Check important commands, that you can use!",
                    colour=config.Success())
            embedVar.add_field(name="General Commands",
                value=f"```{config.prefix}reqabyssmaster uid - To request role Abyss Master``````{config.prefix}getexploration uid - To get the exploration stats```\n",
                                            inline=False)
            embedVar.set_footer(text=f"Requested by {ctx.author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
            embedVar.set_image(
                url=config.banner_success
            )
            await ctx.send(embed=embedVar)
        else:
            # check channel is whitelisted
            whitelist = client_db.find_one('whitelists', {'channel_id': ctx.channel.id})
            if not whitelist:
                return
            
            embedVar = disnake.Embed(
                    title="General Commands!",
                    description="Check important commands, that you can use!",
                    colour=config.Success())
            embedVar.add_field(name="General Commands",
                value=f"```{config.prefix}reqabyssmaster uid - To request role Abyss Master``````{config.prefix}getexploration uid - To get the exploration stats```\n",
                                            inline=False)
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
            message = f"Bot's latency: {round(bot.latency * 1000)}ms"
            message += f"\nBot's websocket rate limited: {bot.is_ws_ratelimited()}"
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
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent

        system_info = f"System: {uname.system}\n"
        system_info += f"Node Name: {uname.node}\n"
        system_info += f"Release: {uname.release}\n"
        system_info += f"Version: {uname.version}\n"
        system_info += f"Machine: {uname.machine}\n"
        system_info += f"Processor: {uname.processor}\n"
        system_info += f"CPU Usage: {cpu_usage}%\n"
        system_info += f"RAM Usage: {ram_usage}%"

        embed = disnake.Embed(
            title="System", description=f"```{system_info}```", color=config.Success())
        embed.set_footer(
            text=f'Command executed by {ctx.author}', icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(embed=errors.create_error_embed(f"{e}"))

        



@bot.command()
async def say(ctx, channel: disnake.TextChannel, *, message: str):
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
async def reqabyssmaster(ctx, uid):
        try:
            # check channel is whitelisted
            whitelist = client_db.find_one('whitelists', {'channel_id': ctx.channel.id})
            if not whitelist:
                return

            # get the user info from genshin api
            if uid == None or uid == "":
                return await ctx.send("Please provide a user id")
                    
            # check uid length must be between 9 and 10
            if len(uid) < 9 or len(uid) > 10:
                return await ctx.send("Please provide a valid user id")
                
            # check if uid is a number
            if not uid.isdigit():
                return await ctx.send("Please provide a valid user id")

            # check if uid registered in the database
            user = client_db.find_one('users_claimed', {'uid': uid, 'server_id': ctx.guild.id})
            if user:
                return await ctx.send("This user has already claimed the Abyss Master role")
                
            cookies = {"ltuid_v2": config.ltuid_v2, "ltoken_v2": config.ltoken_v2}
            client = genshin.Client(cookies)
                
            data_abyss = await client.get_spiral_abyss(uid, previous=False)

            # request to https://enka.network/api/uid/
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://enka.network/api/uid/{uid}") as response:
                    if response.status == 200:
                        data = await response.json()
                        player = data['playerInfo']

                        if player == None:
                            return await ctx.send("Unable to fetch user info")
                            
                        if 'nickname' not in player:
                            player['nickname'] = 'None'
                            
                        if 'level' not in player:
                            player['level'] = 'None'
                            
                        if 'signature' not in player:
                            player['signature'] = 'None'
                            
                        if 'worldLevel' not in player:
                            player['worldLevel'] = 'None'
                            
                        if 'finishAchievementNum' not in player:
                            player['finishAchievementNum'] = 'None'
                            
                        if 'towerFloorIndex' not in player:
                            player['towerFloorIndex'] = 'None'
                            
                        if 'towerLevelIndex' not in player:
                            player['towerLevelIndex'] = 'None'
                            
                        total_stars = data_abyss.total_stars

                        total_battles = data_abyss.total_battles

                        total_wins = data_abyss.total_wins
                            
                        message = ""

                        author = ctx.author
                            
                        # check if floor isn't 12 and chamber isn't 3
                        if int(player['towerFloorIndex']) != 12 or int(player['towerLevelIndex']) != 3:
                            message += "\n> Sorry, I'm unable to grant you the Abyss Master role at the moment :("
                            message += "\n> You are not on Floor 12, Chamber 3."
                            message += "\n> Please try again when you reach Floor 12, Chamber 3."
                            message += "\n> Thank you and good luck!"
                                
                            embedVar = disnake.Embed(
                                    title=f"{player['nickname'] if player['nickname'] else author}'s Info",
                                    colour=config.Error(),
                                    timestamp=datetime.datetime.now())
                            embedVar.add_field(name="<:block_star:1225801267893370961> Abyss Statistics", value="> Fetched from Enka Network and Hoyolab", inline=False)
                            embedVar.add_field(name="<:block_star:1225801267893370961> Name", value=f"> {player['nickname'] if player['nickname'] else 'None'}", inline=False)
                            embedVar.add_field(name="<:block_star:1225801267893370961> Adventure Rank", value=f"> {player['level'] if player['level'] else 'None'}", inline=False)
                            embedVar.add_field(name="<:block_star:1225801267893370961> World Level", value=f"> {player['worldLevel'] if player['worldLevel'] else 'None'}", inline=False)
                            embedVar.add_field(name="<:block_star:1225801267893370961> Abyss Progress", value=f"> {player['towerFloorIndex'] if player['towerFloorIndex'] else 'None'}-{player['towerLevelIndex'] if player['towerLevelIndex'] else 'None'}", inline=False)
                            embedVar.add_field(name="<:block_star:1225801267893370961> Abyss Stars Collected", value=f"> {total_stars} <:abyss_stars:1225579783660765195>", inline=False)
                            embedVar.add_field(name="<:block_star:1225801267893370961> Battles Fought", value=f"> {total_battles}/{total_wins}", inline=False)
                            # embedVar.add_field(name="<:block_star:1225801267893370961> Total Retries", value=f"> {int(total_battles) - int(total_wins)}", inline=False)
                            embedVar.add_field(name="<:block_star:1225801267893370961> Note", value=message, inline=False)
                            embedVar.set_footer(text=f"Requested by {author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
                            embedVar.set_image(
                                url=config.banner_error
                            )

                            return await ctx.send(embed=embedVar)
                        else:
                            if int(total_stars) == 36:
                                message += "\n> Congratulations!"
                                message += "\n> You have achieved 36 <:abyss_stars:1225579783660765195> in Spiral Abyss!"
                                message += "\n> You are eligible for Abyss Master role!"

                                    # give user the Abyss Master role
                                role = disnake.utils.get(ctx.guild.roles, name='Abyss Master')
                                if role:
                                    try:
                                        member = await ctx.guild.fetch_member(author.id)
                                        await member.add_roles(role)
                                    except Exception as e:
                                        print(f'Error adding role to member: {e}')
                                    
                                    # add the user to the database
                                    client_db.insert_one('users_claimed', {'uid': uid, 'user_id': author.id, 'server_id': ctx.guild.id})

                                    embedVar = disnake.Embed(
                                        title=f"{player['nickname'] if player['nickname'] else author}'s Info",
                                        colour=config.Success(),
                                        timestamp=datetime.datetime.now())
                                    embedVar.add_field(name="<:block_star:1225801267893370961> Abyss Statistics", value="> Fetched from Enka Network and Hoyolab", inline=False)
                                    embedVar.add_field(name="<:block_star:1225801267893370961> Name", value=f"> {player['nickname'] if player['nickname'] else 'None'}", inline=False)
                                    embedVar.add_field(name="<:block_star:1225801267893370961> Adventure Rank", value=f"> {player['level'] if player['level'] else 'None'}", inline=False)
                                    embedVar.add_field(name="<:block_star:1225801267893370961> World Level", value=f"> {player['worldLevel'] if player['worldLevel'] else 'None'}", inline=False)
                                    embedVar.add_field(name="<:block_star:1225801267893370961> Abyss Progress", value=f"> {player['towerFloorIndex'] if player['towerFloorIndex'] else 'None'}-{player['towerLevelIndex'] if player['towerLevelIndex'] else 'None'}", inline=False)
                                    embedVar.add_field(name="<:block_star:1225801267893370961> Abyss Stars Collected", value=f"> {total_stars} <:abyss_stars:1225579783660765195>", inline=False)
                                    embedVar.add_field(name="<:block_star:1225801267893370961> Battles Fought", value=f"> {total_battles}/{total_wins}", inline=False)
                                    # embedVar.add_field(name="<:block_star:1225801267893370961> Total Retries", value=f"> {int(total_battles) - int(total_wins)}", inline=False)
                                    embedVar.add_field(name="<:block_star:1225801267893370961> Note", value=message, inline=False)
                                    embedVar.set_footer(text=f"Requested by {author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
                                    embedVar.set_image(
                                        url=config.banner_success
                                    )

                                    return await ctx.send(embed=embedVar)
                            else:
                                message += "\n> Sorry, I'm unable to grant you the Abyss Master role at the moment :("
                                message += "\n> You have not achieved 36 <:abyss_stars:1225579783660765195> in Spiral Abyss!"
                                message += "\n> You are not eligible for Abyss Master role!"
                                message += "\n> Please try again when you reach 36 <:abyss_stars:1225579783660765195>!"
                                message += "\n> Thank you and good luck!"

                                embedVar = disnake.Embed(
                                    title=f"{player['nickname'] if player['nickname'] else author}'s Info",
                                    colour=config.Error(),
                                    timestamp=datetime.datetime.now())
                                embedVar.add_field(name="<:block_star:1225801267893370961> Abyss Statistics", value="> Fetched from Enka Network and Hoyolab", inline=False)
                                embedVar.add_field(name="<:block_star:1225801267893370961> Name", value=f"> {player['nickname'] if player['nickname'] else 'None'}", inline=False)
                                embedVar.add_field(name="<:block_star:1225801267893370961> Adventure Rank", value=f"> {player['level'] if player['level'] else 'None'}", inline=False)
                                embedVar.add_field(name="<:block_star:1225801267893370961> World Level", value=f"> {player['worldLevel'] if player['worldLevel'] else 'None'}", inline=False)
                                embedVar.add_field(name="<:block_star:1225801267893370961> Abyss Progress", value=f"> {player['towerFloorIndex'] if player['towerFloorIndex'] else 'None'}-{player['towerLevelIndex'] if player['towerLevelIndex'] else 'None'}", inline=False)
                                embedVar.add_field(name="<:block_star:1225801267893370961> Abyss Stars Collected", value=f"> {total_stars} <:abyss_stars:1225579783660765195>", inline=False)
                                embedVar.add_field(name="<:block_star:1225801267893370961> Battles Fought", value=f"> {total_battles}/{total_wins}", inline=False)
                                # embedVar.add_field(name="<:block_star:1225801267893370961> Total Retries", value=f"> {int(total_battles) - int(total_wins)}", inline=False)
                                embedVar.add_field(name="<:block_star:1225801267893370961> Note", value=message, inline=False)
                                embedVar.set_footer(text=f"Requested by {author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
                                embedVar.set_image(
                                    url=config.banner_error
                                )

                                return await ctx.send(embed=embedVar)
                    
                    else:
                        return await ctx.send("Error: Unable to fetch user info")
        except Exception as e:
            return await ctx.send(embed=errors.create_error_embed(f"{e}"))

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