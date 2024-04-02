import disnake
from disnake.ext import commands
import os
import config
from helpers import errors
from database.database import Database

client_db = Database(config.mongo)
print("Connected to the database")

class help(commands.Cog):

    def __init__(self, bot):
    	self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Loaded Cog Help')

            
    # Help Command with subcommands 
    @commands.slash_command(name="menu", description="Shows the help command")
    async def menu(inter: disnake.ApplicationCommandInteraction, action: str = commands.Param(choices=["general"])):
        try:
            restricted = client_db.find_one("restrictmode", {"server_id": inter.guild.id})
            if restricted and restricted['status'] == 'on':
                # Check if the channel is whitelisted
                whitelisted = client_db.find_one("whitelists", {"channel_id": inter.channel.id})
                if not whitelisted:
                    return await inter.response.send_message("This command is disabled in this channel", ephemeral=True)
                
                if action == "general":
                    embedVar = disnake.Embed(
                        title="General Commands!",
                        description="Check important commands, that you can use!",
                        colour=config.Success())
                    embedVar.add_field(name="General Commands",
                                        value="```/reqabyssmaster - To request role Abyss Master```\n", 
                                            inline=False)
                    embedVar.set_footer(text="Version: 1.0.0")
                    embedVar.set_image(
                        url="https://i.pinimg.com/564x/2e/57/b4/2e57b4a27aa406a68bc36ee5b14a4ee6.jpg"
                    )
                    await inter.response.send_message(embed=embedVar, ephemeral=True)
            else:
                whitelisted = client_db.find_one("whitelists", {"channel_id": inter.channel.id})
                if not whitelisted:
                    return await inter.response.send_message("This command is disabled in this channel", ephemeral=True)
                
                if action == "general":
                    embedVar = disnake.Embed(
                        title="General Commands!",
                        description="Check important commands, that you can use!",
                        colour=config.Success())
                    embedVar.add_field(name="General Commands",
                                        value="```/reqabyssmaster - To request role Abyss Master```\n", 
                                            inline=False)
                    embedVar.set_footer(text="Version: 1.0.0")
                    embedVar.set_image(
                        url="https://i.pinimg.com/564x/2e/57/b4/2e57b4a27aa406a68bc36ee5b14a4ee6.jpg"
                    )
                    await inter.response.send_message(embed=embedVar, ephemeral=True)
        except Exception as e:
            print(f'Error sending help message: {e}')
            await inter.response.send_message(embed=errors.create_error_embed(f"Error sending help command: {e}"))

def setup(bot):
    bot.add_cog(help(bot))