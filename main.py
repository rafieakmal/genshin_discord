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

# Loading things from config
import config

client_db = Database()
print(f"Connected to the database")

        
# Setting up the bot
bot = commands.Bot(
    command_prefix=config.prefix,
    intents=disnake.Intents.all(),
    case_insensitive=True,
    owner_ids=config.owner_ids
)


# Create Missing Files
db_f = "logging.db"
file_names = ["levels.json", "tags.json", "warns.json"]
dir_path = "data"

for file_name in file_names:
    file_path = os.path.join(dir_path, file_name)

    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding='utf-8') as f:
            f.write("{}")

for db_f in db_f:
    file_path = os.path.join(dir_path, db_f)

    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding='utf-8') as f:
            f.write("")

@bot.command()
async def whitelistadd(ctx, channel: disnake.TextChannel):
    try:
        if ctx.author.id in config.owner_ids:
            # get the channel id from mongodb
            channel_id = client_db.find_one('whitelists', {'channel_id': channel.id})

            # check if the channel is already whitelisted
            if channel_id:
                embed = disnake.Embed(title="Error", description="This channel is already whitelisted!", color=config.Error())
                await ctx.send(embed=embed)
                return

            # insert the channel id to mongodb
            client_db.insert_one('whitelists', {'server_id': ctx.guild.id, 'channel_id': channel.id})
            embed = disnake.Embed(title="Success", description=f"Whitelisted the channel {channel.mention}!", color=config.Success())
            await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while whitelisting the user! {e}", color=config.Error())
        await ctx.send(embed=embed)

@bot.command()
async def denylistadd(ctx, channel: disnake.TextChannel):
    try:
        if ctx.author.id in config.owner_ids:
            # get the channel id from mongodb
            channel_id = client_db.find_one('blacklists', {'channel_id': channel.id})

            # check if the channel is already blacklisted
            if not channel_id:
                embed = disnake.Embed(title="Error", description="This channel is not whitelisted!", color=config.Error())
                await ctx.send(embed=embed)
                return

            # delete the channel id from mongodb
            client_db.delete_one('whitelists', {'channel_id': channel.id})
            embed = disnake.Embed(title="Success", description=f"Denylisted the channel {channel.mention}!", color=config.Success())
            await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while denylisting the channel! {e}", color=config.Error())
        await ctx.send(embed=embed)

@bot.command()
async def whitelistdel(ctx, channel: disnake.TextChannel):
    try:
        if ctx.author.id in config.owner_ids:
            # get the channel id from mongodb
            channel_id = client_db.find_one('whitelists', {'channel_id': channel.id})

            # check if the channel is already whitelisted
            if not channel_id:
                embed = disnake.Embed(title="Error", description="This channel is not whitelisted!", color=config.Error())
                await ctx.send(embed=embed)
                return

            # delete the channel id from mongodb
            client_db.delete_one('whitelists', {'channel_id': channel.id})
            embed = disnake.Embed(title="Success", description=f"Removed the channel {channel.mention} from the whitelist!", color=config.Success())
            await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while removing the channel from the whitelist! {e}", color=config.Error())
        await ctx.send(embed=embed)

@bot.command()
async def denylistdel(ctx, channel: disnake.TextChannel):
    try:
        if ctx.author.id in config.owner_ids:
            # get the channel id from mongodb
            channel_id = client_db.find_one('blacklists', {'channel_id': channel.id})

            # check if the channel is already blacklisted
            if not channel_id:
                embed = disnake.Embed(title="Error", description="This channel is not blacklisted!", color=config.Error())
                await ctx.send(embed=embed)
                return

            # delete the channel id from mongodb
            client_db.delete_one('blacklists', {'channel_id': channel.id})
            embed = disnake.Embed(title="Success", description=f"Removed the channel {channel.mention} from the blacklist!", color=config.Success())
            await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(title="Error", description="You are not allowed to use this command!", color=config.Error())
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
                    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
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
                    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
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
        if ctx.author.id in config.owner_ids:
            whitelist = client_db.find('whitelists', {'server_id': ctx.guild.id})
            if whitelist:
                # tag the channel
                channels = []
                no = 1
                for channel in whitelist:
                    channels.append(f"{no}. <#{channel['channel_id']}>")
                    no += 1
                embed = disnake.Embed(title="Whitelisted Channels", description="\n".join(channels), color=config.Success())
                await ctx.send(embed=embed)
            else:
                embed = disnake.Embed(title="Error", description="No channels are whitelisted!", color=config.Error())
                await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while fetching the whitelist! {e}", color=config.Error())
        await ctx.send(embed=embed)

@bot.command()
async def getclaimedusers(ctx):
    try:
        if ctx.author.id in config.owner_ids:
            users = client_db.find('users_claimed', {'server_id': ctx.guild.id})
            if users:
                # tag the user
                user_list = []
                no = 1
                for user in users:
                    user_list.append(f"{no}. <@{user['user_id']}> - UID: {user['uid']}")
                    no += 1
                embed = disnake.Embed(title="Claimed Users", description="\n".join(user_list), color=config.Success())
                await ctx.send(embed=embed)
            else:
                embed = disnake.Embed(title="Error", description="No users have claimed the Abyss Master role!", color=config.Error())
                await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while fetching the claimed users! {e}", color=config.Error())
        await ctx.send(embed=embed)

@bot.command()
async def getabyssmaster(ctx):
    try:
        if ctx.author.id in config.owner_ids:
            guild = ctx.guild
            role = disnake.utils.get(guild.roles, name='Abyss Master')

            if role:
                member_ids = [member.id for member in guild.members if member.roles and role in member.roles]
                
                # tag the user
                user_list = []
                
                if member_ids:
                    no = 1
                    for member_id in member_ids:
                        user = guild.get_member(member_id)
                        user_list.append(f"{no}. {user.mention}")
                        no += 1
                    embed = disnake.Embed(title="Abyss Master Role", description="\n".join(user_list), color=config.Success())
                    await ctx.send(embed=embed)
                else:
                    embed = disnake.Embed(title="Error", description="No users have Abyss Master role!", color=config.Error())
                    await ctx.send(embed=embed)
        else:
            embed = disnake.Embed(title="Error", description="You are not allowed to use this command!", color=config.Error())
            await ctx.send(embed=embed)
    except Exception as e:
        embed = disnake.Embed(title="Error", description=f"An error occured while fetching the claimed users! {e}", color=config.Error())
        await ctx.send(embed=embed)

@bot.command()
async def resetabyssdata(ctx, uid = None):
    try:
        if ctx.author.id in config.owner_ids:
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
                client_db.delete_all('users_claimed')
                return await ctx.send("Deleted all Abyss Master data from database")
    except Exception as e:
        print(f'Error sending help message: {e}')
        await ctx.send(embed=errors.create_error_embed(f"{e}"))
        

@bot.command()
async def resetabyssrole(ctx, member: disnake.Member):
    try:
        if ctx.author.id in config.owner_ids:
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
        print(f'Error sending help message: {e}')
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

            # cookies = {"ltuid_v2": 133197436, "ltoken_v2": "v2_CAISDGM5b3FhcTNzM2d1OCD9062wBiig8KbvBjD83ME_QgtiYnNfb3ZlcnNlYQ"}
            cookies = {"ltuid_v2": config.ltuid_v2, "ltoken_v2": config.ltoken_v2}
            client = genshin.Client(cookies)
            print(client)
                    
            data_profile = await client.get_genshin_user(uid)

            # print(data_profile.explorations)

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
            
            embed.add_field(name="Note:", value=message_100, inline=False)
            embed.add_field(name="Extra Note:", value=message_data_100, inline=False)
            embed.set_footer(text=f"Requested by {ctx.author}\nBot Version: {config.version}", icon_url=ctx.author.avatar.url)
            embed.set_image(
                url=config.banner_exploration
            )

            await ctx.send(embed=embed)
    except Exception as e:
        print(f'Error sending help message: {e}')
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
        print(f'Error sending help message: {e}')
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
            embedVar.set_footer(text=f"Requested by {ctx.author}\nBot Version: {config.version}", icon_url=ctx.author.avatar.url)
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
            embedVar.set_footer(text=f"Requested by {ctx.author}\nBot Version: {config.version}", icon_url=ctx.author.avatar.url)
            embedVar.set_image(
                url=config.banner_success
            )
            await ctx.send(embed=embedVar)
    except Exception as e:
        print(f'Error sending help message: {e}')
        await ctx.send(embed=errors.create_error_embed(f"{e}"))

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
            # cookies = await client.login_with_password(config.email, config.password)
            # {'cookie_token_v2': 'v2_CAQSDGM5b3FhcTNzM2d1OCD9062wBiiAhbKEBDD83ME_QgtiYnNfb3ZlcnNlYQ', 'account_mid_v2': '1izyx9ekyj_hy', 'account_id_v2': '133197436', 'ltoken_v2': 'v2_CAISDGM5b3FhcTNzM2d1OCD9062wBiig8KbvBjD83ME_QgtiYnNfb3ZlcnNlYQ', 'ltmid_v2': '1izyx9ekyj_hy', 'ltuid_v2': '133197436'}
                
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
                        # message += f"\n\n**User:** {player['nickname'] if player['nickname'] else 'None'}"
                        # message += f"\n**Adventure Rank:** {player['level'] if player['level'] else 'None'}"
                        # message += f"\n**World Level:** {player['worldLevel'] if player['worldLevel'] else 'None'}"
                        # message += f"\n**Abyss Progress:** {player['towerFloorIndex'] if player['towerFloorIndex'] else 'None'}-{player['towerLevelIndex'] if player['towerLevelIndex'] else 'None'}"
                        # message += f"\n**Abyss Stars Collected:** {total_stars} <:abyss_stars:1225579783660765195>"
                        # message += f"\n**Battles Fought:** {total_battles}/{total_wins}"
                        # message += f"\n**Total Retries:** {int(total_battles) - int(total_wins)}"

                        author = ctx.author
                            
                        # check if floor isn't 12 and chamber isn't 3
                        if int(player['towerFloorIndex']) != 12 or int(player['towerLevelIndex']) != 3:
                            message += "\n> Sorry, I'm unable to grant you the Abyss Master role at the moment :("
                            message += "\n> You are not on Floor 12, Chamber 3."
                            message += "\n> Please try again when you reach Floor 12, Chamber 3."
                            message += "\n> Thank you and good luck!"

                                
                            print(f"Total Stars: {total_stars}")

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
                            embedVar.add_field(name="<:block_star:1225801267893370961> Total Retries", value=f"> {int(total_battles) - int(total_wins)}", inline=False)
                            embedVar.add_field(name="<:block_star:1225801267893370961> Note", value=message, inline=False)
                            embedVar.set_footer(text=f"Requested by {author}\nBot Version: {config.version}", icon_url=author.avatar.url)
                            embedVar.set_image(
                                url=config.banner_error
                            )

                            return await ctx.send(embed=embedVar)
                        else:
                            print('User is on Floor 12, Chamber 3')
                            print(f"Total Stars: {total_stars}")
                            if int(total_stars) == 36:
                                message += "\n> Congratulations!"
                                message += "\n> You have achieved 36 <:abyss_stars:1225579783660765195> in Spiral Abyss!"
                                message += "\n> You are eligible for Abyss Master role!"

                                    # give user the Abyss Master role
                                role = disnake.utils.get(ctx.guild.roles, name='Abyss Master')
                                print(role)
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
                                    embedVar.add_field(name="<:block_star:1225801267893370961> Total Retries", value=f"> {int(total_battles) - int(total_wins)}", inline=False)
                                    embedVar.add_field(name="<:block_star:1225801267893370961> Note", value=message, inline=False)
                                    embedVar.set_footer(text=f"Requested by {author}\nBot Version: {config.version}", icon_url=author.avatar.url)
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
                                embedVar.add_field(name="<:block_star:1225801267893370961> Total Retries", value=f"> {int(total_battles) - int(total_wins)}", inline=False)
                                embedVar.add_field(name="<:block_star:1225801267893370961> Note", value=message, inline=False)
                                embedVar.set_footer(text=f"Requested by {author}\nBot Version: {config.version}", icon_url=author.avatar.url)
                                embedVar.set_image(
                                    url=config.banner_error
                                )

                                return await ctx.send(embed=embedVar)
                    
                    else:
                        return await ctx.send("Error: Unable to fetch user info")
        except Exception as e:
            print(f'Error sending userinfo message: {e}')
            return await ctx.send(embed=errors.create_error_embed(f"{e}"))

# On Ready
@bot.event
async def on_ready():
    print("The bot is ready!")
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator} | {bot.user.id}')
    print(f"I am on {len(bot.guilds)} server")
    print(f'Running on {platform.system()} {platform.release()} ({os.name})')
    print(f'Bot Version: {config.version}')
    print(f"Disnake version : {disnake.__version__}")
    print(f"Python version: {platform.python_version()}")
    print('================== Loaded Cogs ================')
    status_task.start()
    await asyncio.sleep(0.01)
    print('===============================================')

# Status Task
@tasks.loop(minutes=0.15)
async def status_task():
    await bot.change_presence(activity=disnake.Game(random.choice(config.activity)))

# Load Cogs On Start
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

# A slash command to reload cogs
@bot.slash_command(name="reload", description="Reloads a cog")
async def reload(inter: disnake.ApplicationCommandInteraction, cog: str):
    try:
        if inter.author.id in config.owner_ids:
            try:
                bot.reload_extension(f"cogs.{cog}")
                embed = disnake.Embed(title="Success", description=f"Reloaded {cog}", color=config.Success())
                embed.set_footer(text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url)
                embed.set_thumbnail(url=inter.guild.me.avatar.url)
                await inter.send(embed=embed, ephemeral=True)
            except Exception as e:
                embed = disnake.Embed(title="Error", description=f"Failed to reload {cog} because of {e}", color=config.Error())
                embed.set_footer(text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url)
                embed.set_thumbnail(url=inter.guild.me.avatar.url)
                await inter.send(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(title="Error", description="You are not allowed to use this command!", color=config.Error())
            embed.set_footer(text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url)
            embed.set_thumbnail(url=inter.guild.me.avatar.url)
            await inter.send(embed=embed, ephemeral=True)
    except Exception as e:
        print(f'An error occured while reloading a cog! {e}')

# A slash command to load cogs
@bot.slash_command(name="load", description="Loads a cog")
async def load(inter: disnake.ApplicationCommandInteraction, cog: str):
    try:
        if inter.author.id in config.owner_ids:
            try:
                bot.load_extension(f"cogs.{cog}")
                embed = disnake.Embed(title="Success", description=f"Loaded {cog}", color=config.Success())
                embed.set_footer(text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url)
                embed.set_thumbnail(url=inter.guild.me.avatar.url)
                await inter.send(embed=embed, ephemeral=True)
            except Exception as e:
                embed = disnake.Embed(title="Error", description=f"Failed to load {cog} because of {e}", color=config.Error())
                embed.set_footer(text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url)
                embed.set_thumbnail(url=inter.guild.me.avatar.url)
                await inter.send(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(title="Error", description="You are not allowed to use this command!", color=config.Error())
            embed.set_footer(text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url)
            embed.set_thumbnail(url=inter.guild.me.avatar.url)
            await inter.send(embed=embed, ephemeral=True)
    except Exception as e:
        print(f'An error occured while loading a cog! {e}')

# A slash command to unload cogs
@bot.slash_command(name="unload", description="Unloads a cog")
async def unload(inter: disnake.ApplicationCommandInteraction, cog: str):
    try:
        if inter.author.id in config.owner_ids:
            try:
                bot.unload_extension(f"cogs.{cog}")
                embed = disnake.Embed(title="Success", description=f"Unloaded {cog}", color=config.Success())
                embed.set_footer(text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url)
                embed.set_thumbnail(url=inter.guild.me.avatar.url)
                await inter.send(embed=embed, ephemeral=True)
            except Exception as e:
                embed = disnake.Embed(title="Error", description=f"Failed to unload {cog} because of {e}", color=config.Error())
                embed.set_footer(text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url)
                embed.set_thumbnail(url=inter.guild.me.avatar.url)
                await inter.send(embed=embed, ephemeral=True)
        else:
            embed = disnake.Embed(title="Error", description="You are not allowed to use this command!", color=config.Error())
            embed.set_footer(text=f"Requested by {inter.author}", icon_url=inter.author.avatar.url)
            embed.set_thumbnail(url=inter.guild.me.avatar.url)
            await inter.send(embed=embed, ephemeral=True)
    except Exception as e:
        print(f'An error occured while unloading a cog! {e}')
    
# Run The Bot 
bot.run(config.token, reconnect=True)