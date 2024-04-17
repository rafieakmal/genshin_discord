from disnake.ext import tasks, commands
import time, config, disnake, datetime
from database.database import Database
import asyncio

# create a database object
client_db = Database()

class TaskCustom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.task_custom.start()

    def cog_unload(self):
        self.task_custom.cancel()

    async def remove_roles_and_notify(self, **kwargs):  
        member_ids = [member.id for member in kwargs['guild'].members if kwargs['role'] in member.roles]
        if member_ids:
            await asyncio.gather(*(member.remove_roles(kwargs['role']) for member in filter(None, (kwargs['guild'].get_member(member_id) for member_id in member_ids))))
            await client_db.delete_many('users_claimed', {})
            message = (
                "**Morning Travelers!**\n\n"
                "Today is the day of the Abyss reset!\n"
                "I have removed the Abyss Master role from all members who had it before.\n\n"
                "Good luck on your floor clears and I hope you get 36 <:abyss_stars:1225579783660765195>!\n"
                "Remember, travelers! The time has come to reclaim your rightful place as the Abyss Master. "
                f"Use the command ``/reqabyssmaster`` in the <#{config.request_abyss_master_channel}> channel and let your power be known!"
            )
            embed = disnake.Embed(
                title="Abyss Reset Notification",
                description=message,
                colour=config.Success(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Genshin Impact Indonesia Helper\nBot Version: {config.version}", icon_url=config.icon_url_front)
            embed.set_image(url=config.abyss_header)
            await kwargs['channel'].send(embed=embed)
        else:
            await client_db.delete_many('users_claimed', {})

    @tasks.loop(time=datetime.time(hour=3, minute=0, second=0, tzinfo=datetime.timezone(datetime.timedelta(hours=7))))
    async def task_custom(self):
        now = datetime.datetime.now()
        if now.day in (1, 16):
            guild = self.bot.get_guild(config.guild)
            role = disnake.utils.get(guild.roles, name='Abyss Master')
            channel = self.bot.get_channel(config.broadcast_channel)
            await self.remove_roles_and_notify(guild=guild, role=role, channel=channel)

    @task_custom.before_loop
    async def before_task_custom(self):
        print('Waiting to start custom task...')
        await self.bot.wait_until_ready()
        
def setup(bot):
    bot.add_cog(TaskCustom(bot))
