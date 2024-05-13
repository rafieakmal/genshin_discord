from disnake.ext import tasks, commands
import time, config, disnake, datetime
from database.database import Database
import asyncio

# Create a database object to interact with the database
client_db = Database()

class TaskCustom(commands.Cog):
    """
    A custom task class that inherits from commands.Cog to manage scheduled tasks.
    """
    def __init__(self, bot):
        """
        Initializes the TaskCustom class with a bot instance and starts the task loop.
        
        Parameters:
            bot: The bot instance to which this Cog will be attached.
        """
        self.bot = bot
        self.task_custom.start()

    def cog_unload(self):
        """
        Cancels the task loop when the Cog is unloaded.
        """
        self.task_custom.cancel()

    async def remove_roles_and_notify(self, **kwargs):
        """
        Removes a specified role from all members in a guild and sends a notification in a specified channel.
        
        Parameters:
            kwargs: A dictionary containing 'guild', 'role', and 'channel' keys.
        """
        # Collect member IDs who have the specified role
        member_ids = [member.id for member in kwargs['guild'].members if kwargs['role'] in member.roles]
        
        # If there are members with the role, proceed to remove the role and notify
        if member_ids:
            # Remove the role from all members asynchronously
            await asyncio.gather(*(member.remove_roles(kwargs['role']) for member in filter(None, (kwargs['guild'].get_member(member_id) for member_id in member_ids))))
            # Delete all documents from 'users_claimed' collection
            await client_db.delete_many('users_claimed', {})
            # Prepare the notification message
            message = (
                "**Morning Travelers!**\n\n"
                "Today is the day of the Abyss reset!\n"
                "I have removed the Abyss Master role from all members who had it before.\n\n"
                "Good luck on your floor clears and I hope you get 36 <:abyss_stars:1225579783660765195>!\n"
                "Remember, travelers! The time has come to reclaim your rightful place as the Abyss Master. "
                f"Use the command ``/reqabyssmaster`` in the <#{config.request_abyss_master_channel}> channel and let your power be known!"
            )
            # Create an embed message for the notification
            embed = disnake.Embed(
                title="Abyss Reset Notification",
                description=message,
                colour=config.Success(),
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(text=f"Genshin Impact Indonesia Helper\nBot Version: {config.version}", icon_url=config.icon_url_front)
            embed.set_image(url=config.abyss_header)
            # Send the notification in the specified channel
            await kwargs['channel'].send(embed=embed)
        else:
            # If no members had the role, just clear the 'users_claimed' collection
            await client_db.delete_many('users_claimed', {})

    @tasks.loop(time=datetime.time(hour=3, minute=0, second=0, tzinfo=datetime.timezone(datetime.timedelta(hours=7))))
    async def task_custom(self):
        """
        A scheduled task that runs at 3:00 AM (UTC+7) and performs role management and notifications on specific days.
        """
        now = datetime.datetime.now()
        # Check if the current day is the 1st or 16th
        if now.day in (1, 16):
            guild = self.bot.get_guild(config.guild)
            role = disnake.utils.get(guild.roles, name='Abyss Master')
            channel = self.bot.get_channel(config.broadcast_channel)
            # Call the function to remove roles and send notifications
            await self.remove_roles_and_notify(guild=guild, role=role, channel=channel)

    @task_custom.before_loop
    async def before_task_custom(self):
        """
        A pre-loop preparation function that prints a waiting message and ensures the bot is ready.
        """
        print('Waiting to start custom task...')
        await self.bot.wait_until_ready()
        
def setup(bot):
    """
    Setup function to add this Cog to the bot.
    
    Parameters:
        bot: The bot instance to which this Cog will be added.
    """
    bot.add_cog(TaskCustom(bot))
