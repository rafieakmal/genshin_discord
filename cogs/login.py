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
import sys
import random
from disnake import TextInputStyle

# Connecting to the database
client_db = Database()
print("Connected to the database")

def restart_program():
    print("Restarting the program...")
    last_python = sys.executable
    os.execl(last_python, last_python, *sys.argv)

# Subclassing the modal.
class LoginModal(disnake.ui.Modal):
    def __init__(self):
        # The details of the modal, and its components
        components = [
            disnake.ui.TextInput(
                label="Email",
                placeholder="Your HoYoLAB Email",
                custom_id="email",
                style=TextInputStyle.short,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Password",
                placeholder="Your HoYoLAB Password",
                custom_id="password",
                style=TextInputStyle.short,
            ),
        ]
        super().__init__(title="Login to HoYoLAB", components=components)

    # The callback received when the user input is completed.
    async def callback(self, inter: disnake.ModalInteraction):
        try:
            author = inter.author
            await inter.response.send_message("Logging in...", ephemeral=True)
            last_message_id = await inter.original_response()
            print(last_message_id)

            embed = disnake.Embed(title="HoYoLAB Login", color=0x00FF00)
            email = ""
            password = ""

            for key, value in inter.text_values.items():
                embed.add_field(
                    name=key.capitalize(),
                    value=value[:1024],
                    inline=False,
                )
                if key == "email":
                    email += value
                elif key == "password":
                    password += value

            print(f"Email: {email} | Password: {password}")
            try:
                client = genshin.Client()
                port_randomize = random.randint(5000, 9000)
                cookies = await client.login_with_password(email, password, port=port_randomize)
                if cookies:
                    os.system(f'netstat -ano | findstr :{port_randomize} | findstr /B 0.0.0.0')
                    # Save the cookies to the database
                    data = {
                        "user_id": author.id,
                        "user_name": author.name,
                        "ltuid": cookies["ltuid_v2"],
                        "ltoken": cookies["ltoken_v2"],
                        "cookie_token": cookies["cookie_token_v2"],
                        "account_id": cookies["account_id_v2"],
                        "account_mid": cookies["account_mid_v2"],
                        "ltmid": cookies["ltmid_v2"],

                    }

                    # save data to database
                    client_db.insert_one('users', data)

                    embedVar = disnake.Embed(
                        title="HoYoLAB Login",
                        description="You have successfully logged in to HoYoLAB",
                        colour=config.Success(),
                        timestamp=datetime.datetime.now())
                    embedVar.set_footer(text=f"Requested by {inter.author}\nBot Version: {config.version}", icon_url=config.icon_url_front)

                    await inter.followup.send(embed=embedVar, ephemeral=True)
                else:
                    os.system(f'netstat -ano | findstr :{port_randomize} | findstr /B 0.0.0.0')
                    await inter.followup.send(embed=errors.create_error_embed("Error Logging in to HoYoLAB"))
            except Exception as e:
                await inter.send(embed=errors.create_error_embed(f"{e}"))
                restart_program()
        except Exception as e:
            await inter.send(embed=errors.create_error_embed(f"{e}"))
            restart_program()

class login(commands.Cog):
    
    def __init__(self, bot):
    	self.bot = bot
        
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded Cog Login')

    # Ping Command
    @commands.slash_command(name='login', description='Login to HoYoLAB Server')
    async def login(self, inter: disnake.ApplicationCommandInteraction):
        try:
            author = inter.author

            # Check if the user is already logged in
            user = client_db.find_one('users', {'user_id': author.id})
            if user:
                return await inter.send(embed=errors.create_error_embed("You are already logged in to HoYoLAB!"))
            
            await inter.response.send_modal(LoginModal())
        except Exception as e:
            print(f'Error Sending Ping Command: {e}')
            await inter.send(embed=errors.create_error_embed(f"{e}"))
                
def setup(bot):
    bot.add_cog(login(bot))