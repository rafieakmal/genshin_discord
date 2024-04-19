# Importing the required modules
import disnake
from disnake.ext import commands
import os
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
import base64

# Connecting to the database
client_db = Database()

async def restart_program():
    print("Restarting the program asynchronously...")
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

            email = inter.text_values["email"]
            password = inter.text_values["password"]

            client = genshin.Client()
            port_randomize = random.randint(5000, 9000)
            try:
                cookies = await client.login_with_password(email, password, port=port_randomize)
                if cookies:
                    password_bytes = password.encode("ascii")
                    password_encoded = base64.b64encode(password_bytes)
                    password_encoded = password_encoded.decode("ascii")

                    data = {
                        "user_id": author.id,
                        "user_name": author.name,
                        "email": email,
                        "password": password_encoded,
                        **{key: cookies[key] for key in cookies if key.endswith("_v2")},
                    }

                    await client_db.insert_one('users', data)

                    embedVar = disnake.Embed(
                        title="HoYoLAB Login",
                        description="You have successfully logged in to HoYoLAB",
                        colour=config.Success(),
                        timestamp=datetime.datetime.now())
                    embedVar.set_footer(text=f"Requested by {inter.author}\nBot Version: {config.version}", icon_url=config.icon_url_front)

                    await inter.followup.send(embed=embedVar, ephemeral=True)
                else:
                    await inter.followup.send(embed=errors.create_error_embed("Error Logging in to HoYoLAB"))
            except Exception as e:
                await inter.send(embed=errors.create_error_embed(f"Login failed: {e}"), ephemeral=True)
                await restart_program()
        except Exception as e:
            await inter.send(embed=errors.create_error_embed(f"Unexpected error: {e}"), ephemeral=True)
            await restart_program()

class login(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name='login', description='Login to HoYoLAB Server')
    async def login(self, inter: disnake.ApplicationCommandInteraction):
        try:
            author = inter.author

            # Check if the user is already logged in
            user = await client_db.find_one('users', {'user_id': author.id})
            if user:
                await inter.send(embed=errors.create_error_embed("You are already logged in to HoYoLAB!"), ephemeral=True)
                return
            
            await inter.response.send_modal(LoginModal())
        except Exception as e:
            await inter.send(embed=errors.create_error_embed(f"Error: {e}"), ephemeral=True)
                
def setup(bot):
    bot.add_cog(login(bot))