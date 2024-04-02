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

    # user info command
    @commands.slash_command(name='reqabyssmaster', description='Request the Abyss Master role')
    async def reqabyssmaster(self, inter: disnake.ApplicationCommandInteraction, uid: str):
        try:
            is_error = False
            restricted = client_db.find_one('restrictmode', {'server_id': inter.guild.id})
            if restricted and restricted['status'] == 'on':
                # check channel is whitelisted
                whitelist = client_db.find_one('whitelists', {'channel_id': inter.channel.id})
                if not whitelist:
                    return await inter.response.send_message("This command is disabled in this channel", ephemeral=True)
                
                # get the user info from genshin api
                if uid == None or uid == "":
                    return await inter.response.send_message("Please provide a user id", ephemeral=True)
                    
                # check uid length must be between 9 and 10
                if len(uid) < 9 or len(uid) > 10:
                    return await inter.response.send_message("Please provide a valid user id", ephemeral=True)
                    
                # check if uid is a number
                if not uid.isdigit():
                    return await inter.response.send_message("Please provide a valid user id", ephemeral=True)
                
                # check if uid registered in the database
                user = client_db.find_one('users_claimed', {'server_id': inter.guild.id, 'uid': uid})
                if user:
                    return await inter.response.send_message("This user has already claimed the Abyss Master role")
                    
                # cookies = {"ltuid_v2": 133197436, "ltoken_v2": "v2_CAISDGM5b3FhcTNzM2d1OBokZGYxODE1ZjEtOTYwMi00NDU4LWE2NzctZDU5NjJjOTNiODVhIOijqbAGKNPj5_4EMPzcwT9CC2Jic19vdmVyc2Vh"}
                client = genshin.Client()
                cookies = await client.login_with_password(config.email, config.password)
                print(cookies)
                    
                data_abyss = await client.get_spiral_abyss(uid, previous=False)

                print(data_abyss)

                    # request to https://enka.network/api/uid/
                await inter.response.send_message("Loading...")
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
                                
                            message = "Fetched from Enka Network and Hoyolab"
                            message += f"\n\n**User:** ```{player['nickname'] if player['nickname'] else 'None'}```"
                            message += f"\n**Adventure Rank:** ```{player['level'] if player['level'] else 'None'}```"
                            message += f"\n**Signature:** ```{player['signature'] if player['signature'] else 'None'}```"
                            message += f"\n**World Level:** ```{player['worldLevel'] if player['worldLevel'] else 'None'}```"
                            message += f"\n**Achievements:** ```{player['finishAchievementNum'] if player['finishAchievementNum'] else 'None'}```"
                            message += f"\n**Floor:** ```{player['towerFloorIndex'] if player['towerFloorIndex'] else 'None'}```"
                            message += f"\n**Chamber:** ```{player['towerLevelIndex'] if player['towerLevelIndex'] else 'None'}```"
                            message += f"\n**Total Stars:** ```{total_stars}```"
                            message += f"\n**Total Battles:** ```{total_battles}```"
                            message += f"\n**Total Wins:** ```{total_wins}```"

                            author = inter.author
                                
                            # check if floor isn't 12 and chamber isn't 3
                            if int(player['towerFloorIndex']) != 12 or int(player['towerLevelIndex']) != 3:
                                print('User is not on Floor 12, Chamber 3')
                                message += f"\n\n**Requesting Abyss Master role for UID: {uid}**"
                                message += "\n**Note:** User is not on Floor 12, Chamber 3"
                                message += "\n**Conclusion:** User is not eligible for Abyss Master role"

                                    
                                print(f"Total Stars: {total_stars}")

                                is_error = False
                            else:
                                print('User is on Floor 12, Chamber 3')
                                print(f"Total Stars: {total_stars}")
                                if int(total_stars) == 36:
                                    print('User has 9 stars')
                                    message += "\n\n**Congratulations!**"
                                    message += "\n**You have achieved 36 stars in Spiral Abyss!**"
                                    message += "\n**You are eligible for Abyss Master role!**"

                                        # give user the Abyss Master role
                                    role = disnake.utils.get(inter.guild.roles, name='Abyss Master')
                                    print(role)
                                    if role:
                                        try:
                                            member = await inter.guild.fetch_member(author.id)
                                            await member.add_roles(role)
                                        except Exception as e:
                                            print(f'Error adding role to member: {e}')
                                            return await inter.response.send_message(embed=errors.create_error_embed(f"{e}"))
                                            

                                        # embedVar = disnake.Embed(
                                        #     title=f"{player['nickname'] if player['nickname'] else author}'s Info",
                                        #     description=f"Requesting Abyss Master role for user with id: {uid}",
                                        #     colour=config.Success())
                                        # embedVar.add_field(name="User Info", value=message, inline=False)
                                        # embedVar.set_footer(text="Version: 1.0.0")
                                        # embedVar.set_image(
                                        #     url=config.banner_success
                                        # )

                                        # add the user to the database
                                        client_db.insert_one('users_claimed', {'uid': uid, 'user_id': author.id, 'server_id': inter.guild.id})

                                        # await inter.response.send_message(embed=embedVar)
                                        is_error = True
                                else:
                                    print('User has less than 9 stars')
                                    message += "\n\n**You have not achieved 36 stars in Spiral Abyss!**"
                                    message += "\n**You are not eligible for Abyss Master role!**"

                                    
                                
                                if is_error:
                                    embedVar = disnake.Embed(
                                            title=f"{player['nickname'] if player['nickname'] else author}'s Info",
                                            description=f"Requesting Abyss Master role for user with id: {uid}",
                                            colour=config.Error())
                                    embedVar.add_field(name="User Info", value=message, inline=False)
                                    embedVar.set_footer(text="Version: 1.0.0")
                                    embedVar.set_image(
                                        url=config.banner_error
                                    )
                                else:
                                    embedVar = disnake.Embed(
                                        title=f"{player['nickname'] if player['nickname'] else author}'s Info",
                                        description=f"Requesting Abyss Master role for user: {uid}",
                                        colour=config.Success())
                                    embedVar.add_field(name="User Info", value=message, inline=False)
                                    embedVar.set_footer(text="Version: 1.0.0")
                                    embedVar.set_image(
                                        url=config.banner_success
                                    )

                                print(embedVar)


                                return await inter.response.send_message(embed=embedVar)

                        else:
                            return await inter.response.send_message("Unable to fetch user info")
                        
            else:
                print('Restricted mode is off')
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
                
                last_message = await inter.response.send_message("Please sit tight while I fetch your info")
                last_message_id = await inter.original_response()
                print(last_message_id)

                # cookies = {"ltuid_v2": 133197436, "ltoken_v2": "v2_CAISDGM5b3FhcTNzM2d1OBokZGYxODE1ZjEtOTYwMi00NDU4LWE2NzctZDU5NjJjOTNiODVhIOijqbAGKNPj5_4EMPzcwT9CC2Jic19vdmVyc2Vh"}
                # client = genshin.Client()
                # cookies = await client.login_with_password(config.email, config.password)
                cookies = {"ltuid_v2": 133197436, "ltoken_v2": "v2_CAISDGM5b3FhcTNzM2d1OCD9062wBiig8KbvBjD83ME_QgtiYnNfb3ZlcnNlYQ"}
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
                                
                            message = "Fetched from Enka Network and Hoyolab"
                            message += f"\n\n**User:** ```{player['nickname'] if player['nickname'] else 'None'}```"
                            message += f"\n**Signature:** ```{player['signature'] if player['signature'] else 'None'}```"
                            message += f"\n**World Level:** ```{player['worldLevel'] if player['worldLevel'] else 'None'}```"
                            message += f"\n**Abyss Progress:** ```{player['towerFloorIndex'] if player['towerFloorIndex'] else 'None'}-{player['towerLevelIndex'] if player['towerLevelIndex'] else 'None'}```"
                            message += f"\n**Abyss Stars Collected:** ```{total_stars} Stars```"
                            message += f"\n**Battles Fought:** ```{total_battles}/{total_wins}```"
                            message += f"\n**Total Retries:** ```{int(total_battles) - int(total_wins)}```"

                            author = inter.author
                                
                            # check if floor isn't 12 and chamber isn't 3
                            if int(player['towerFloorIndex']) != 12 or int(player['towerLevelIndex']) != 3:
                                print('User is not on Floor 12, Chamber 3')
                                message += "\n\n**I'm unable to grant you the Abyss Master role at the moment.**"
                                message += "\n**You are not on Floor 12, Chamber 3.**"
                                message += "\n**Please try again when you reach Floor 12, Chamber 3.**"
                                message += "\n**Thank you and good luck!**"

                                    
                                print(f"Total Stars: {total_stars}")

                                is_error = True
                            else:
                                print('User is on Floor 12, Chamber 3')
                                print(f"Total Stars: {total_stars}")
                                if int(total_stars) == 36:
                                    print('User has 9 stars')
                                    message += "\n\n**Congratulations!**"
                                    message += "\n**You have achieved 36 stars in Spiral Abyss!**"
                                    message += "\n**You are eligible for Abyss Master role!**"

                                        # give user the Abyss Master role
                                    role = disnake.utils.get(inter.guild.roles, name='Abyss Master')
                                    print(role)
                                    if role:
                                        try:
                                            member = await inter.guild.fetch_member(author.id)
                                            await member.add_roles(role)
                                        except Exception as e:
                                            print(f'Error adding role to member: {e}')
                                        
                                        # add the user to the database
                                        client_db.insert_one('users_claimed', {'uid': uid, 'user_id': author.id, 'server_id': inter.guild.id})

                                        is_error = False
                                else:
                                    print('User has less than 9 stars')
                                    message += "\n\n**I'm unable to grant you the Abyss Master role at the moment.**"
                                    message += "\n**You have not achieved 36 stars in Spiral Abyss!**"
                                    message += "\n**You are not eligible for Abyss Master role!**"
                                    message += "\n**Please try again when you reach 36 stars.**"
                                    message += "\n**Thank you and good luck!**"

                                    is_error = True
                            
                            if is_error:
                                embedVar = disnake.Embed(
                                        title=f"{player['nickname'] if player['nickname'] else author}'s Info",
                                        description=f"Requesting Abyss Master role for user with id: {uid}",
                                        colour=config.Error())
                                embedVar.add_field(name="User Info", value=message, inline=False)
                                embedVar.set_footer(text="Version: 1.0.0")
                                embedVar.set_image(
                                    url=config.banner_error
                                )
                            else:
                                embedVar = disnake.Embed(
                                    title=f"{player['nickname'] if player['nickname'] else author}'s Info",
                                    description=f"Requesting Abyss Master role for user: {uid}",
                                    colour=config.Success())
                                embedVar.add_field(name="User Info", value=message, inline=False)
                                embedVar.set_footer(text="Version: 1.0.0")
                                embedVar.set_image(
                                    url=config.banner_success
                                )

                            # edit the message from the last message id
                            await last_message_id.edit(embed=embedVar)
                        
                        else:
                            await last_message_id.edit_original_response(content="Unable to fetch user info")
        except Exception as e:
            print(f'Error sending userinfo message: {e}')
            await inter.response.send_message(embed=errors.create_error_embed(f"{e}"))


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