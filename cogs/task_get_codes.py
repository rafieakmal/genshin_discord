from disnake.ext import tasks, commands
import aiohttp

from database.database import Database

# Initialize a database object globally to avoid multiple initializations
client_db = Database()

class TaskGetCodes(commands.Cog):
    """
    A class to fetch and store redeemable codes for Genshin Impact from a specified URL.
    This class is a Cog for a discord bot, making use of discord.py's tasks extension for periodic tasks.
    """
    def __init__(self, bot):
        self.bot = bot
        self.get_codes.start()  # Start the periodic task when the cog is initialized

    def cog_unload(self):
        """
        Clean up when the cog is unloaded.
        Specifically, cancel the get_codes task to prevent it from running after the cog is unloaded.
        """
        self.get_codes.cancel()

    @tasks.loop(minutes=1.0)
    async def get_codes(self):
        """
        Periodically fetches redeemable codes from a specified URL and stores them in a database if they are not already present.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get('https://hoyo-codes.vercel.app/codes?game=genshin') as response:
                if response.status == 200:
                    data = await response.json()
                    new_codes = data.get('codes', [])
                    for code in new_codes:
                        # Check if the code already exists in the database to avoid duplicates
                        if not await client_db.find_one('redeem_codes', {'code': code}):
                            await client_db.insert_one('redeem_codes', {'code': code})
                else:
                    print('Failed to fetch data')
    
    @get_codes.before_loop
    async def before_get_codes(self):
        """
        A pre-task hook that runs before the get_codes task starts.
        Ensures that the bot is fully ready before starting the task.
        """
        print('Waiting to start getting redeem codes...')
        await self.bot.wait_until_ready()

def setup(bot):
    """
    A setup function required by discord.py's cog system.
    Adds the TaskGetCodes cog to the bot.
    """
    bot.add_cog(TaskGetCodes(bot))
