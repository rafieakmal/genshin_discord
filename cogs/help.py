import disnake
from disnake.ext import commands
import os
import config
from helpers import errors
from database.database import Database
import datetime

client_db = Database()

class help(commands.Cog):

    def __init__(self, bot):
    	self.bot = bot

            
    # Help Command with subcommands 
    @commands.slash_command(name="menu", description="Shows the help command")
    async def menu(inter: disnake.ApplicationCommandInteraction, action: str = commands.Param(choices=["general"])):
        try:
            whitelisted = client_db.find_one("whitelists", {"channel_id": inter.channel.id})
            if not whitelisted:
                return await inter.response.send_message("This command is disabled in this channel", ephemeral=True)
                
            if action == "general":
                embedVar = disnake.Embed(
                    title="General Commands!",
                    description="Check important commands, that you can use!",
                    colour=config.Success(),
                    timestamp=datetime.datetime.now())
                embedVar.add_field(name="General Commands",
                    value="```/reqabyssmaster - To request role Abyss Master``````/getexploration - To get the exploration stats```\n",
                    inline=False)
                embedVar.set_footer(text=f"Requested by {inter.author}\nBot Version: {config.version}", icon_url=inter.author.avatar.url)
                embedVar.set_image(
                    url="https://i.pinimg.com/564x/2e/57/b4/2e57b4a27aa406a68bc36ee5b14a4ee6.jpg"
                )
                await inter.response.send_message(embed=embedVar, ephemeral=True)
        except Exception as e:
            print(f'Error sending help message: {e}')
            await inter.response.send_message(embed=errors.create_error_embed(f"Error sending help command: {e}"))

def setup(bot):
    bot.add_cog(help(bot))