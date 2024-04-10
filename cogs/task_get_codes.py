from disnake.ext import tasks, commands
import time, genshin, config, disnake, datetime
from database.database import Database
import aiohttp, asyncio

# create a database object
client_db = Database()
print('Connected to the database')


class task_get_codes(commands.Cog):
    def __init__(self, bot):
        self.index = 0
        self.bot = bot
        self.message_id = 0
        self.get_codes.start()

    def cog_unload(self):
        self.get_codes.cancel()

    @tasks.loop(minutes=1.0)
    async def get_codes(self):
         # request to retrieve the redeemable codes
        print('Fetching redeem codes...')
        async with aiohttp.ClientSession() as session:
            async with session.get('https://hoyo-codes.vercel.app/codes?game=genshin') as response:
                if response.status == 200:
                    data = await response.json()
                    if 'codes' in data:
                        # insert to database
                        for code in data['codes']:
                            if client_db.find_one('redeem_codes', {'code': code}):
                                pass
                            else:
                                client_db.insert_one('redeem_codes', {'code': code})
                else:
                    print('Failed to fetch data')
    
    @get_codes.before_loop
    async def before_printer_codes(self):
        print('Waiting to start getting redeem codes...')
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(task_get_codes(bot))
