from disnake.ext import tasks, commands
import time, genshin, config, disnake, datetime
from database.database import Database
import aiohttp, asyncio

# create a database object
client_db = Database()

class task_customm(commands.Cog):
    def __init__(self, bot):
        self.index = 0
        self.bot = bot
        self.message_id = 0
        self.task_custom.start()

    def cog_unload(self):
        self.task_custom.cancel()

    
    @tasks.loop(seconds=1.0)
    async def task_custom(self):
        # get the current time with timezones
        now = time.time()
        
        # format the time
        current_time = time.strftime('%H:%M:%S', time.localtime(now))

        # get current date
        date = time.strftime('%d/%m/%Y', time.localtime(now))
        day = time.strftime('%A', time.localtime(now))
        month = time.strftime('%B', time.localtime(now))
        year = time.strftime('%Y', time.localtime(now))
        day_raw = time.strftime('%d', time.localtime(now))
        month_raw = time.strftime('%m', time.localtime(now))
        year_raw = time.strftime('%Y', time.localtime(now))

        # if day raw equals to 1 and 16
        if day_raw in ('01', '16'):
            # time must be 03:00:00
            if current_time == '03:01:01':
                # get members in the role of the guild id=1051526111135272990
                guild = self.bot.get_guild(config.guild)
                
                # get the role
                role = disnake.utils.get(guild.roles, name='Abyss Master')

                member_ids = [member.id for member in guild.members if member.roles and role in member.roles]
                
                # reset the role
                if member_ids:
                    for member_id in member_ids:
                        member = guild.get_member(member_id)
                        await member.remove_roles(role)
                    
                    # delete all users from the database
                    await client_db.delete_many('users_claimed', {})
                    
                    # get the channel
                    channel = self.bot.get_channel(config.broadcast_channel)
                    
                    # send the message
                    message_builder = "**Morning Travelers!**"
                    message_builder += "\n\nToday is the day of the Abyss reset!"
                    message_builder += "\nI have removed the Abyss Master role from all members who had it before"
                    message_builder += "\n\nGood luck on your floor clears and I hope you get 36 <:abyss_stars:1225579783660765195>!"
                    message_builder += "\nRemember, travelers! The time has come to reclaim your rightful place as the Abyss Master. Use the command ``/reqabyssmaster``"
                    message_builder += "\nin the <#1065702573971091477> channel and let your power be known!"

                    embedVar = disnake.Embed(
                        title="Abyss Reset Notification",
                        description=message_builder,
                        colour=config.Success(),
                        timestamp=datetime.datetime.now()
                    )
                    embedVar.set_footer(text=f"Genshin Impact Indonesia Helper\nBot Version: {config.version}", icon_url=config.icon_url_front)
                    embedVar.set_image(url=config.abyss_header)

                    await channel.send(embed=embedVar)
                else:
                    await client_db.delete_many('users_claimed', {})

                    channel = self.bot.get_channel(config.broadcast_channel)
                    
                    message_builder = "**Morning Travelers!**"
                    message_builder += "\n\nToday is the day of the Abyss reset!"
                    message_builder += "\nI have removed the Abyss Master role from all members who had it before"
                    message_builder += "\n\nGood luck on your floor clears and I hope you get 36 <:abyss_stars:1225579783660765195>!"
                    message_builder += "\nRemember, travelers! The time has come to reclaim your rightful place as the Abyss Master. Use the command ``/reqabyssmaster``"
                    message_builder += "\nin the <#1065702573971091477> channel and let your power be known!"

                    embedVar = disnake.Embed(
                        title="Abyss Reset Notification",
                        description=message_builder,
                        colour=config.Success(),
                        timestamp=datetime.datetime.now()
                    )
                    embedVar.set_footer(text=f"Genshin Impact Indonesia Helper\nBot Version: {config.version}", icon_url=config.icon_url_front)
                    embedVar.set_image(url=config.abyss_header)

                    await channel.send(embed=embedVar)

    @task_custom.before_loop
    async def before_printer_rewards(self):
        print('Waiting to start custom task...')
        await self.bot.wait_until_ready()
        
def setup(bot):
    bot.add_cog(task_customm(bot))
