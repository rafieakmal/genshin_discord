# Importing the required modules
import disnake
from disnake.ext import commands, tasks
import os
import psutil 
import requests
import json
import aiohttp
import config
from helpers import errors
import genshin
from database.database import Database
import asyncio
import datetime

# Connecting to the database
client_db = Database()

class general(commands.Cog):
    
    def __init__(self, bot):
    	self.bot = bot

    # Ping Command
    @commands.slash_command(name='ping', description='Get the bot\'s latency')
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        try:
            embed = disnake.Embed(title=f"Pong!", description=f"The ping is around `{round(self.bot.latency * 1000)}ms`", color=config.Success())
            embed.set_footer(text=f'Command executed by {inter.author}', icon_url=inter.author.avatar.url)
            await inter.response.send_message(ephemeral=True, embed=embed)
        except Exception as e:
            await inter.send(embed=errors.create_error_embed(f"Error sending ping command: {e}"))

    @commands.slash_command(name='getexploration', description='Get the exploration progress of a user')
    async def getexploration(self, inter: disnake.ApplicationCommandInteraction, uid: str):
        await inter.response.defer()
        await asyncio.sleep(3)
        try:
            if uid == None or uid == "":
                await inter.edit_original_response("Please provide a user id")
                    
            # check uid length must be between 9 and 10
            if len(uid) < 9 or len(uid) > 10:
                await inter.edit_original_response("Please provide a valid user id")
                
                # check if uid is a number
            if not uid.isdigit():
                await inter.edit_original_response("Please provide a valid user id")


            user_logged_in = client_db.find_one('users', {'user_id': inter.author.id})
            if user_logged_in:
                cookies = {
                    "ltuid_v2": user_logged_in['ltuid'],
                    "ltoken_v2": user_logged_in['ltoken'],
                    "cookie_token_v2": user_logged_in['cookie_token'],
                    "account_id_v2": user_logged_in['account_id'],
                    "account_mid_v2": user_logged_in['account_mid'],
                    "ltmid_v2": user_logged_in['ltmid'],
                }
            else:
                cookies = {"ltuid_v2": config.ltuid_v2, "ltoken_v2": config.ltoken_v2}

            client = genshin.Client(cookies)
                    
            data_profile = await client.get_genshin_user(uid)

            data_exploration = []

            for exploration in data_profile.explorations:
                # exclude data Chenyu Vale
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
                message_100 += "Congratulations! All explorations are 100% completed!"
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

            author = inter.author
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
            embed.set_footer(text=f"Requested by {inter.author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
            embed.set_image(
                url=config.banner_exploration
            )

            await inter.edit_original_response(embed=embed)
        except Exception as e:
            await inter.edit_original_response(embed=errors.create_error_embed(f"{e}"))

    @commands.slash_command(name='broadcast', description='Broadcast a message to a channel')
    async def broadcast(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel, message: str):
        try:
            if inter.author.id not in config.owner_ids:
                return await inter.response.send_message("You need to have the `Bot Owner` role to use this command", ephemeral=True)
            await inter.response.defer()
            embedVar = disnake.Embed(
                title="Hi Traveler!",
                description="This is a message from your favorite person!",
                colour=config.Success(),
                timestamp=datetime.datetime.now())
            embedVar.add_field(name="<:block_star:1225801267893370961> Message", value=f"> {message}", inline=False)
            embedVar.set_thumbnail(
                url='https://cdn.wanderer.moe/genshin-impact/emotes/teyvat-times--series-emojis-5.png'
            )
            embedVar.set_footer(text=f"Bot Version: {config.version}", icon_url=config.icon_url_front)
            await channel.send(embed=embedVar)
            await inter.edit_original_response(content=f"Message sent to {channel.mention}")
        except Exception as e:
            await inter.edit_original_response(embed=errors.create_error_embed(f"{e}"))

    # add codes manually
    @commands.slash_command(name='addcode', description='Add a redeem code manually')
    async def addcode(self, inter: disnake.ApplicationCommandInteraction, code: str):
        try:
            if inter.author.id not in config.owner_ids:
                return await inter.response.send_message("You need to have the `Bot Owner` role to use this command", ephemeral=True)
            await inter.response.defer()
            if code == None or code == "":
                return await inter.edit_original_response("Please provide a redeem code")
            if client_db.find_one('redeem_codes', {'code': code}):
                return await inter.edit_original_response("This code has already been added")
            client_db.insert_one('redeem_codes', {'code': code})
            await inter.edit_original_response(content=f"Code `{code}` has been added successfully!")
        except Exception as e:
            await inter.edit_original_response(embed=errors.create_error_embed(f"{e}"))
    
    @commands.slash_command(name='daily', description='Claims your daily reward')
    async def daily(self, inter: disnake.ApplicationCommandInteraction, action: str = commands.Param(choices=["genshin", "honkai impact 3rd", "honkai star rail"])):
        # get logged in user
        try:
            author = inter.author
            await inter.response.defer()
            await asyncio.sleep(3)
            # check if user has already claimed the daily reward
            user = client_db.find_one('users', {'user_id': author.id})
            if user:
                cookies = {
                    "ltuid_v2": user['ltuid'],
                    "ltoken_v2": user['ltoken'],
                    "cookie_token_v2": user['cookie_token'],
                    "account_id_v2": user['account_id'],
                    "account_mid_v2": user['account_mid'],
                    "ltmid_v2": user['ltmid'],
                }

                # get the client
                client = genshin.Client(debug=True)
                client.set_cookies(cookies)
                if action == "genshin":
                    client.default_game = genshin.Game.GENSHIN
                elif action == "honkai impact 3rd":
                    client.default_game = genshin.Game.HONKAI
                elif action == "honkai star rail":
                    client.default_game = genshin.Game.STARRAIL

                # get the daily check-in

                signed_in, claimed_rewards = await client.get_reward_info()

                if signed_in:
                    await inter.edit_original_response(content="You have already claimed your daily reward!")
                else:
                    try:
                        reward = await client.claim_daily_reward()
                    except genshin.InvalidCookies:
                        await inter.edit_original_response(content="Invalid cookies.")
                    except genshin.GeetestTriggered:
                        print("Geetest triggered on daily reward.")
                    except genshin.AlreadyClaimed:
                        await inter.edit_original_response(content="You have already claimed your daily reward!")
                    else:
                        embedVar = disnake.Embed(
                            title="Your daily reward has been claimed!",
                            colour=config.Success(),
                            timestamp=datetime.datetime.now())
                        embedVar.add_field(name="<:block_star:1225801267893370961> Reward", value=f"> {reward.name}", inline=True)
                        embedVar.add_field(name="<:block_star:1225801267893370961> Amount", value=f"> {reward.amount}x", inline=True)
                        embedVar.set_footer(text=f"Requested by {author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
                        embedVar.set_thumbnail(
                            url=reward.icon
                        )

                        await inter.edit_original_response(embed=embedVar)
        except Exception as e:
            await inter.response.send_message(embed=errors.create_error_embed(f"{e}"), ephemeral=True)

    # user info command
    @commands.slash_command(name='reqabyssmaster', description='Request the Abyss Master role')
    async def reqabyssmaster(self, inter: disnake.ApplicationCommandInteraction, uid: str):
        await inter.response.defer()
        await asyncio.sleep(3)
        try:
            is_error = False

            # check channel is whitelisted
            whitelist = client_db.find_one('whitelists', {'channel_id': inter.channel.id})
            if not whitelist:
                return
            
            # get the user info from genshin api
            if uid == None or uid == "":
                return await inter.edit_original_response("Please provide a user id")
                        
            # check uid length must be between 9 and 10
            if len(uid) < 9 or len(uid) > 10:
                return await inter.edit_original_response("Please provide a valid user id")
                    
            # check if uid is a number
            if not uid.isdigit():
                return await inter.edit_original_response("Please provide a valid user id")

            # check if uid registered in the database
            user = client_db.find_one('users_claimed', {'uid': uid, 'server_id': inter.guild.id})
            if user:
                return await inter.edit_original_response("This user has already claimed the Abyss Master role")
                
            user_logged_in = client_db.find_one('users', {'user_id': inter.author.id})
            if user_logged_in:
                cookies = {
                    "ltuid_v2": user_logged_in['ltuid'],
                    "ltoken_v2": user_logged_in['ltoken'],
                    "cookie_token_v2": user_logged_in['cookie_token'],
                    "account_id_v2": user_logged_in['account_id'],
                    "account_mid_v2": user_logged_in['account_mid'],
                    "ltmid_v2": user_logged_in['ltmid'],
                }
            else:
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
                            return await inter.response.send_message(f"Unable to fetch user info")
                                
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

                        author = inter.author
                                
                        # check if floor isn't 12 and chamber isn't 3
                        if int(player['towerFloorIndex']) != 12 or int(player['towerLevelIndex']) != 3:
                            message += "\n> Sorry, I'm unable to grant you the Abyss Master role at the moment :("
                            message += "\n> You are not on Floor 12, Chamber 3."
                            message += "\n> Please try again when you reach Floor 12, Chamber 3."
                            message += "\n> Thank you and good luck!"

                            is_error = True
                        else:
                            if int(total_stars) == 36:
                                message += "\n> Congratulations!"
                                message += "\n> You have achieved 36 <:abyss_stars:1225579783660765195> in Spiral Abyss!"
                                message += "\n> You are eligible for Abyss Master role!"

                                # give user the Abyss Master role
                                role = disnake.utils.get(inter.guild.roles, name='Abyss Master')
                                if role:
                                    try:
                                        member = await inter.guild.fetch_member(author.id)
                                        await member.add_roles(role)
                                    except Exception as e:
                                        print(f'Error adding role to member: {e}')
                                        await inter.edit_original_response(content="Unable to add Abyss Master role to user")
                                        
                                    # add the user to the database
                                    client_db.insert_one('users_claimed', {'uid': uid, 'user_id': author.id, 'server_id': inter.guild.id})

                                    is_error = False
                                else:
                                    message += "\n> Sorry, I'm unable to grant you the Abyss Master role at the moment :("
                                    message += "\n> You have not achieved 36 <:abyss_stars:1225579783660765195> in Spiral Abyss!"
                                    message += "\n> You are not eligible for Abyss Master role!"
                                    message += "\n> Please try again when you reach 36 <:abyss_stars:1225579783660765195>!"
                                    message += "\n> Thank you and good luck!"

                                    is_error = True
                            
                        if is_error:
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
                        else:
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

                        # edit the message from the last message id
                        await inter.edit_original_response(embed=embedVar)
                        
                    else:
                        await inter.edit_original_response(content="Unable to fetch user info")
        except Exception as e:
            await inter.edit_original_response(embed=errors.create_error_embed(f"{e}"))


    # invite the bot to your server
    @commands.slash_command(name='invite',
                            description='Invite the bot to your server',)
    async def invite(self, inter: disnake.ApplicationCommandInteraction):
        try:
            embed = disnake.Embed(title="Invite Me", color=config.Success())
            embed.add_field (name="Invite Link", value=f"[Click Here](https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands)", inline=False)
            embed.set_footer(text=f'Requested by {inter.author}', icon_url=config.icon_url_front)
            await inter.response.send_message(embed=embed)
        except Exception as e:
            await inter.send(embed=errors.create_error_embed(f"Error sending invite command: {e}"))
                
def setup(bot):
    bot.add_cog(general(bot))