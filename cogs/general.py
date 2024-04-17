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
        # Check if the command is used in a whitelisted channel or DMs
        channel_id = inter.channel_id if inter.channel else inter.user.id
        whitelisted = await client_db.find_one("whitelists", {"channel_id": channel_id})
        if not whitelisted:
            return await inter.response.send_message("This command is disabled in this channel or DM", ephemeral=True)
        
        try:
            # Calculate the latency and check if the websocket is rate limited
            latency_ms = round(self.bot.latency * 1000)
            is_rate_limited = self.bot.is_ws_ratelimited()
            
            # Construct the response message
            message = f"Websocket's latency: {latency_ms}ms\nWebsocket's rate limited: {is_rate_limited}"
            embed = disnake.Embed(title="PONG!", description=message, color=config.Success())
            embed.set_footer(text=f'Command executed by {inter.author}', icon_url=inter.author.avatar.url)
            
            # Send the response
            await inter.response.send_message(embed=embed)
        except Exception as e:
            # Handle any exceptions by sending an error message
            await inter.send(embed=errors.create_error_embed(f"Error sending ping command: {e}"))

    @commands.slash_command(name='getexploration', description='Get the exploration progress of a user')
    async def getexploration(self, inter: disnake.ApplicationCommandInteraction, uid: str):
        # Check if the command is used in a whitelisted channel or DMs
        channel_id = inter.channel_id if inter.channel else inter.user.id
        whitelisted = await client_db.find_one("whitelists", {"channel_id": channel_id})
        if not whitelisted:
            return await inter.response.send_message("This command is disabled in this channel or DM", ephemeral=True)

        await inter.response.defer()
        if not uid or not uid.isdigit() or not (9 <= len(uid) <= 10):
            return await inter.edit_original_response(content="Please provide a valid user id")

        try:
            user_logged_in = await client_db.find_one('users', {'user_id': inter.author.id})
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

            all_data_are_100 = all(exploration['exploration_percentage'] == 100 for exploration in data_exploration)
            message_100 = "> Congratulations! All explorations are 100% completed!" if all_data_are_100 else ""

            incomplete_explorations = [exploration['name'] for exploration in data_exploration if exploration['exploration_percentage'] != 100]
            message_100 += "\n> Explorations that are not 100% completed:\n" + "\n".join([f"> - {name}" for name in incomplete_explorations])

            complete_explorations = [exploration['name'] for exploration in data_exploration if exploration['exploration_percentage'] == 100]
            message_data_100 = "\n> Explorations that are 100% completed:\n" + "\n".join([f"> - {name}" for name in complete_explorations])

            data_emoji_progress = config.data_emoji_progress  # Assuming this is defined in the config file for better maintainability

            embed = disnake.Embed(title=f"{inter.author.name}'s Exploration Progress", color=config.Success(), timestamp=datetime.datetime.now())
            for exploration in data_exploration:
                progress_emoji = self.get_progress_emoji(exploration['exploration_percentage'], data_emoji_progress)
                embed.add_field(
                    name=f"<:block_star:1225801267893370961> {exploration['name']} - <:world_level:1225721002588114954> {exploration['level']}",
                    value=f"\n> Progress: {exploration['exploration_percentage']}%\n> {progress_emoji}",
                    inline=False
                )

            embed.add_field(name="<:block_star:1225801267893370961> Note", value=message_100, inline=False)
            embed.add_field(name="<:block_star:1225801267893370961> Extra Note", value=message_data_100, inline=False)
            embed.set_footer(text=f"Requested by {inter.author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
            embed.set_image(url=config.banner_exploration)

            await inter.edit_original_response(embed=embed)
        except Exception as e:
            await inter.edit_original_response(embed=errors.create_error_embed(f"{e}"))

    def get_progress_emoji(self, percentage, emoji_dict):
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

    @commands.slash_command(name='broadcast', description='Broadcast a message to a channel')
    async def broadcast(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel, message: str):
        """
        Broadcasts a message to a specified channel with an embed format.
        This command can only be used by the bot owners or staff members of the server.

        Parameters:
        - inter: The interaction context.
        - channel: The text channel where the message will be broadcasted.
        - message: The message to be broadcasted.
        """
        # Check if the command is used in a server context
        if not inter.guild:
            return await inter.response.send_message("This command can only be used in a server.", ephemeral=True)

        try:
            # Retrieve staff IDs for the server
            staff_ids = await client_db.get_staffs_in_server(inter.guild.id)
            # Check if the user has the required permissions
            if inter.author.id not in config.owner_ids and inter.author.id not in staff_ids:
                return await inter.response.send_message("You don't have the permission to use this command", ephemeral=True)
            
            await inter.response.defer()
            # Create the embed message
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
            # Send the embed message to the specified channel
            await channel.send(embed=embedVar)
            # Confirm the broadcast to the command user
            await inter.edit_original_response(content=f"Message sent to {channel.mention}")
        except Exception as e:
            # Handle any exceptions and send an error message
            await inter.edit_original_response(embed=errors.create_error_embed(f"{e}"))
    
    @commands.slash_command(name='say', description='Say a message to a channel')
    async def say(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel, message: str):
        """
        Sends a message to a specified channel with a simple format.
        This command can only be used by the bot owners or staff members of the server.

        Parameters:
        - inter: The interaction context.
        - channel: The text channel where the message will be sent.
        - message: The message to be sent.
        """
        if not inter.guild:
            return await inter.response.send_message("This command can only be used in a server.", ephemeral=True)
        
        try:
            # Retrieve staff IDs for the server
            staff_ids = await client_db.get_staffs_in_server(inter.guild.id)
            # Check if the user has the required permissions
            if inter.author.id not in config.owner_ids and inter.author.id not in staff_ids:
                return await inter.response.send_message("You don't have the permission to use this command", ephemeral=True)
            
            await inter.response.defer()
            # Send the message to the specified channel
            await channel.send(message)
            # Confirm the message sending to the command user
            await inter.edit_original_response(content=f"Message sent to {channel.mention}")
        except Exception as e:
            # Handle any exceptions and send an error message
            await inter.edit_original_response(embed=errors.create_error_embed(f"{e}"))

    @commands.slash_command(name='reply', description='Reply to a message in a channel')
    async def reply(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel, message_id: str, message: str):
        """
        Replies to a specific message in a channel.
        This command can only be used by the bot owners or staff members of the server.

        Parameters:
        - inter: The interaction context.
        - channel: The text channel containing the message to reply to.
        - message_id: The ID of the message to reply to.
        - message: The reply message.
        """
        if not inter.guild:
            return await inter.response.send_message("This command can only be used in a server.", ephemeral=True)
        
        try:
            # Retrieve staff IDs for the server
            staff_ids = await client_db.get_staffs_in_server(inter.guild.id)
            # Check if the user has the required permissions
            if inter.author.id not in config.owner_ids and inter.author.id not in staff_ids:
                return await inter.response.send_message("You don't have the permission to use this command", ephemeral=True)
            
            await inter.response.defer()
            # Fetch the message to reply to
            message_to_reply = await channel.fetch_message(message_id)
            if not message_to_reply:
                return await inter.edit_original_response(content="Message not found.")
            # Send the reply to the specified message
            await message_to_reply.reply(message)
            # Confirm the reply to the command user
            await inter.edit_original_response(content=f"Replied to the message in {channel.mention}")
        except Exception as e:
            # Handle any exceptions and send an error message
            await inter.edit_original_response(embed=errors.create_error_embed(f"{e}"))

    # add codes manually
    @commands.slash_command(name='addcode', description='Add a redeem code manually')
    async def addcode(self, inter: disnake.ApplicationCommandInteraction, code: str):
        try:
            # Check if the command is used in a server or DMs and set appropriate staff_ids
            if inter.guild:
                staff_ids = await client_db.get_staffs_in_server(inter.guild.id)
            else:
                staff_ids = []

            if inter.author.id not in config.owner_ids and inter.author.id not in staff_ids:
                return await inter.response.send_message("You don't have the permission to use this command", ephemeral=True)
            await inter.response.defer()
            if code == None or code == "":
                return await inter.edit_original_response("Please provide a redeem code")
            if await client_db.find_one('redeem_codes', {'code': code}):
                return await inter.edit_original_response("This code has already been added")
            await client_db.insert_one('redeem_codes', {'code': code})
            await inter.edit_original_response(content=f"Code `{code}` has been added successfully!")
        except Exception as e:
            await inter.edit_original_response(embed=errors.create_error_embed(f"{e}"))
    
    @commands.slash_command(name='daily', description='Claims your daily reward')
    async def daily(self, inter: disnake.ApplicationCommandInteraction, action: str = commands.Param(choices=["genshin", "honkai impact 3rd", "honkai star rail"])):
        """
        Handles the daily reward claim for different games.
        
        Parameters:
        - inter: The interaction context.
        - action: The game for which the daily reward is being claimed.
        """
        try:
            await inter.response.defer()
            user = await client_db.find_one('users', {'user_id': inter.author.id})
            if not user:
                await inter.edit_original_response(content="User not found.")
                return

            # Construct cookies from user data
            cookies = {key: user[key] for key in ['ltuid_v2', 'ltoken_v2', 'cookie_token_v2', 'account_id_v2', 'account_mid_v2', 'ltmid_v2']}

            # Initialize the client with cookies
            client = genshin.Client()
            client.set_cookies(cookies)

            # Set the default game based on the action
            game_map = {
                "genshin": genshin.Game.GENSHIN,
                "honkai impact 3rd": genshin.Game.HONKAI,
                "honkai star rail": genshin.Game.STARRAIL
            }
            client.default_game = game_map[action]

            # Attempt to claim the daily reward
            try:
                reward = await client.claim_daily_reward()
            except genshin.AlreadyClaimed:
                await inter.edit_original_response(content="You have already claimed your daily reward!")
                return
            except (genshin.InvalidCookies, genshin.GeetestTriggered) as e:
                await inter.edit_original_response(content=f"Failed to claim daily reward: {e}")
                return

            # Prepare and send the success response
            embedVar = disnake.Embed(
                title="Your daily reward has been claimed!",
                colour=config.Success(),
                timestamp=datetime.datetime.now())
            embedVar.add_field(name="Reward", value=f"> {reward.name}", inline=True)
            embedVar.add_field(name="Amount", value=f"> {reward.amount}x", inline=True)
            embedVar.set_footer(text=f"Requested by {inter.author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
            embedVar.set_thumbnail(url=reward.icon)

            await inter.edit_original_response(embed=embedVar)
        except Exception as e:
            await inter.response.send_message(embed=errors.create_error_embed(f"Error: {e}"), ephemeral=True)

    # user info command
    @commands.slash_command(name='reqabyssmaster', description='Request the Abyss Master role')
    async def reqabyssmaster(self, inter: disnake.ApplicationCommandInteraction, uid: str):
        """
        This command allows users to request the Abyss Master role based on their Spiral Abyss performance.
        It checks if the user meets the criteria (Floor 12, Chamber 3, 36 stars) before granting the role.
        
        Parameters:
        - inter: The interaction context.
        - uid: The user's game UID.
        """
        channel_id = inter.channel_id if inter.channel else False
        whitelisted = await client_db.find_one("whitelists", {"channel_id": channel_id})
        if not whitelisted:
            return await inter.response.send_message("This command is disabled in this channel or DM", ephemeral=True)
        
        await inter.response.defer()

        # Validate UID input
        if not uid or not uid.isdigit() or not (9 <= len(uid) <= 10):
            return await inter.edit_original_response(content="Please provide a valid user id")

        # Check if the channel is whitelisted
        whitelist = await client_db.find_one('whitelists', {'channel_id': inter.channel.id})
        if not whitelist:
            return await inter.edit_original_response(content="This command is not allowed in this channel.")

        # Fetch user data from the database
        user_claimed = await client_db.find_one('users_claimed', {'uid': uid, 'server_id': inter.guild.id})
        if user_claimed:
            return await inter.edit_original_response(content="This user has already claimed the Abyss Master role")

        user_logged_in = await client_db.find_one('users', {'user_id': inter.author.id})

        if not user_logged_in:
            cookies = {"ltuid_v2": config.ltuid_v2, "ltoken_v2": config.ltoken_v2}
        else:
            # Set up Genshin client with user's cookies
            cookies = {key: user_logged_in[key] for key in [
                'ltuid_v2', 'ltoken_v2', 'cookie_token_v2', 'account_id_v2', 'account_mid_v2', 'ltmid_v2']}
            
        client = genshin.Client(cookies=cookies)

        # Fetch Spiral Abyss data
        try:
            data_abyss = await client.get_spiral_abyss(uid, previous=False)
        except Exception as e:
            return await inter.edit_original_response(content=f"Failed to fetch Spiral Abyss data: {e}")

        # Fetch user info from Enka Network
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://enka.network/api/uid/{uid}") as response:
                if response.status != 200:
                    return await inter.edit_original_response(content="Unable to fetch user info from Enka Network.")
                data = await response.json()

        player = data.get('playerInfo', {})
        nickname = player.get('nickname', 'None')
        level = player.get('level', 'None')
        world_level = player.get('worldLevel', 'None')
        tower_floor_index = player.get('towerFloorIndex', 'None')
        tower_level_index = player.get('towerLevelIndex', 'None')

        # Check if user meets the criteria for Abyss Master role
        if int(tower_floor_index) != 12 or int(tower_level_index) != 3 or int(data_abyss.total_stars) < 36:
            message = "> You do not meet the criteria for the Abyss Master role."
            embed_color = config.Error()
            banner_url = config.banner_error
        else:
            # Grant Abyss Master role
            role = disnake.utils.get(inter.guild.roles, name='Abyss Master')
            if role:
                member = await inter.guild.fetch_member(inter.author.id)
                await member.add_roles(role)
                await client_db.insert_one('users_claimed', {'uid': uid, 'user_id': inter.author.id, 'server_id': inter.guild.id})
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
            colour=embed_color,
            timestamp=datetime.datetime.now())
        embedVar.add_field(name="<:block_star:1225801267893370961> Adventure Rank", value=f"> {level}", inline=False)
        embedVar.add_field(name="<:block_star:1225801267893370961> World Level", value=f"> {world_level}", inline=False)
        embedVar.add_field(name="<:block_star:1225801267893370961> Abyss Progress", value=f"> Floor {tower_floor_index} - Chamber {tower_level_index}", inline=False)
        embedVar.add_field(name="<:block_star:1225801267893370961> Abyss Stars Collected",
                           value=f"> {data_abyss.total_stars} <:abyss_stars:1225579783660765195>", inline=False)
        embedVar.add_field(name="<:block_star:1225801267893370961> Note", value=message, inline=False)
        embedVar.set_footer(text=f"Requested by {inter.author}\nBot Version: {config.version}", icon_url=config.icon_url_front)
        embedVar.set_image(url=banner_url)

        await inter.edit_original_response(embed=embedVar)


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

