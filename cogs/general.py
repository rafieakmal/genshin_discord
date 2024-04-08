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
print("Connected to the database")

class general(commands.Cog):
    
    def __init__(self, bot):
    	self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded Cog General')

    # Ping Command
    @commands.slash_command(name='ping', description='Get the bot\'s latency')
    async def ping(self, inter: disnake.ApplicationCommandInteraction):
        try:
            embed = disnake.Embed(title=f"Pong!", description=f"The ping is around `{round(self.bot.latency * 1000)}ms`", color=config.Success())
            embed.set_footer(text=f'Command executed by {inter.author}', icon_url=inter.author.avatar.url)
            await inter.response.send_message(ephemeral=True, embed=embed)
        except Exception as e:
            print(f'Error Sending Ping Command: {e}')
            await inter.send(embed=errors.create_error_embed(f"Error sending ping command: {e}"))

    @commands.slash_command(name='getexploration', description='Get the exploration progress of a user')
    async def getexploration(self, inter: disnake.ApplicationCommandInteraction, uid: str):
        try:
            if uid == None or uid == "":
                await inter.response.send_message("Please provide a valid user id", ephemeral=True)
                    
            # check uid length must be between 9 and 10
            if len(uid) < 9 or len(uid) > 10:
                await inter.response.send_message("Please provide a valid user id", ephemeral=True)
                
                # check if uid is a number
            if not uid.isdigit():
                await inter.response.send_message("Please provide a valid user id", ephemeral=True)

            await inter.response.send_message("Please sit tight while I fetch your info")
            last_message_id = await inter.original_response()
            print(last_message_id)

            # cookies = {"ltuid_v2": 133197436, "ltoken_v2": "v2_CAISDGM5b3FhcTNzM2d1OCD9062wBiig8KbvBjD83ME_QgtiYnNfb3ZlcnNlYQ"}
            cookies = {"ltuid_v2": config.ltuid_v2, "ltoken_v2": config.ltoken_v2}
            client = genshin.Client(cookies)
            print(client)
                    
            data_profile = await client.get_genshin_user(uid)

            # print(data_profile.explorations)

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
            embed.set_footer(text=f"Requested by {inter.author}\nBot Version: {config.version}", icon_url=inter.author.avatar.url)
            embed.set_image(
                url=config.banner_exploration
            )

            await last_message_id.edit(embed=embed)
        except Exception as e:
            print(f'Error sending help message: {e}')
            await inter.followup.send(embed=errors.create_error_embed(f"{e}"))

    # user info command
    @commands.slash_command(name='reqabyssmaster', description='Request the Abyss Master role')
    async def reqabyssmaster(self, inter: disnake.ApplicationCommandInteraction, uid: str):
        try:
            is_error = False

            # check channel is whitelisted
            whitelist = client_db.find_one('whitelists', {'channel_id': inter.channel.id})
            if not whitelist:
                return
            
            # get the user info from genshin api
            if uid == None or uid == "":
                await inter.response.send_message("Please provide a user id", ephemeral=True)
                        
            # check uid length must be between 9 and 10
            if len(uid) < 9 or len(uid) > 10:
                await inter.response.send_message("Please provide a valid user id", ephemeral=True)
                    
            # check if uid is a number
            if not uid.isdigit():
                await inter.response.send_message("Please provide a valid user id", ephemeral=True)

            # check if uid registered in the database
            user = client_db.find_one('users_claimed', {'uid': uid, 'server_id': inter.guild.id})
            if user:
                print('User has already claimed Abyss Master role')
                return await inter.response.send_message("This user has already claimed the Abyss Master role")
                
            await inter.response.send_message("Please sit tight while I fetch your info")
            last_message_id = await inter.original_response()
            print(last_message_id)

            # cookies = {"ltuid_v2": 133197436, "ltoken_v2": "v2_CAISDGM5b3FhcTNzM2d1OBokZGYxODE1ZjEtOTYwMi00NDU4LWE2NzctZDU5NjJjOTNiODVhIOijqbAGKNPj5_4EMPzcwT9CC2Jic19vdmVyc2Vh"}
            # client = genshin.Client()
            # cookies = await client.login_with_password(config.email, config.password)
            # cookies = {"ltuid_v2": 133197436, "ltoken_v2": "v2_CAISDGM5b3FhcTNzM2d1OCD9062wBiig8KbvBjD83ME_QgtiYnNfb3ZlcnNlYQ"}
            cookies = {"ltuid_v2": config.ltuid_v2, "ltoken_v2": config.ltoken_v2}
            client = genshin.Client(cookies)
            print(client)
                    
            data_abyss = await client.get_spiral_abyss(uid, previous=False)

            print(data_abyss)

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
                        # message += f"\n\n**User:** {player['nickname'] if player['nickname'] else 'None'}"
                        # message += f"\n**Adventure Rank:** {player['level'] if player['level'] else 'None'}"
                        # message += f"\n**World Level:** {player['worldLevel'] if player['worldLevel'] else 'None'}"
                        # message += f"\n**Abyss Progress:** {player['towerFloorIndex'] if player['towerFloorIndex'] else 'None'}-{player['towerLevelIndex'] if player['towerLevelIndex'] else 'None'}"
                        # message += f"\n**Abyss Stars Collected:** {total_stars} <:abyss_stars:1225579783660765195>"
                        # message += f"\n**Battles Fought:** {total_battles}/{total_wins}"
                        # message += f"\n**Total Retries:** {int(total_battles) - int(total_wins)}"

                        author = inter.author
                                
                        # check if floor isn't 12 and chamber isn't 3
                        if int(player['towerFloorIndex']) != 12 or int(player['towerLevelIndex']) != 3:
                            # print('User is not on Floor 12, Chamber 3')
                            message += "\n> Sorry, I'm unable to grant you the Abyss Master role at the moment :("
                            message += "\n> You are not on Floor 12, Chamber 3."
                            message += "\n> Please try again when you reach Floor 12, Chamber 3."
                            message += "\n> Thank you and good luck!"

                                    
                            # print(f"Total Stars: {total_stars}")

                            is_error = True
                        else:
                            # print('User is on Floor 12, Chamber 3')
                            # print(f"Total Stars: {total_stars}")
                            if int(total_stars) == 36:
                                # print('User has 9 stars')
                                message += "\n> Congratulations!"
                                message += "\n> You have achieved 36 <:abyss_stars:1225579783660765195> in Spiral Abyss!"
                                message += "\n> You are eligible for Abyss Master role!"

                                # give user the Abyss Master role
                                role = disnake.utils.get(inter.guild.roles, name='Abyss Master')
                                print(role)
                                if role:
                                    try:
                                        member = await inter.guild.fetch_member(author.id)
                                        await member.add_roles(role)
                                    except Exception as e:
                                        print(f'Error adding role to member: {e}')
                                        await last_message_id.edit_original_response(content="Unable to add Abyss Master role to user")
                                        
                                    # add the user to the database
                                    client_db.insert_one('users_claimed', {'uid': uid, 'user_id': author.id, 'server_id': inter.guild.id})

                                    is_error = False
                                else:
                                    # print('User has less than 9 stars')
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
                            embedVar.set_footer(text=f"Requested by {author}\nBot Version: {config.version}", icon_url=author.avatar.url)
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
                            embedVar.set_footer(text=f"Requested by {author}\nBot Version: {config.version}", icon_url=author.avatar.url)
                            embedVar.set_image(
                                url=config.banner_success
                            )

                        # edit the message from the last message id
                        await last_message_id.edit(embed=embedVar)
                        
                    else:
                        await last_message_id.edit_original_response(content="Unable to fetch user info")
        except Exception as e:
            # print(f'Error sending userinfo message: {e}')
            await inter.followup.send(embed=errors.create_error_embed(f"{e}"))


    # invite the bot to your server
    @commands.slash_command(name='invite',
                            description='Invite the bot to your server',)
    async def invite(self, inter: disnake.ApplicationCommandInteraction):
        try:
            embed = disnake.Embed(title="Invite Me", color=config.Success())
            embed.add_field (name="Invite Link", value=f"[Click Here](https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands)", inline=False)
            embed.set_footer(text=f'Requested by {inter.author}', icon_url=inter.author.avatar.url)
            await inter.response.send_message(embed=embed)
        except Exception as e:
            print(f'Error sending invite message: {e}')
            await inter.send(embed=errors.create_error_embed(f"Error sending invite command: {e}"))
                
def setup(bot):
    bot.add_cog(general(bot))