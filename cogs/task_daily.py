from disnake.ext import tasks, commands
import time, genshin, config, disnake, datetime
from database.database import Database
import aiohttp, asyncio

# create a database object
client_db = Database()

class task_daily(commands.Cog):
    def __init__(self, bot):
        self.index = 0
        self.bot = bot
        self.message_id = 0
        self.daily_task.start()

    def cog_unload(self):
        self.daily_task.cancel()

    
    @tasks.loop(seconds=1.0)
    async def daily_task(self):
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

        if current_time == '23:01:00':
            # get all users token
            users = client_db.find('users', {})
            if users:
                for user in users:
                    cookies = {
                        "ltuid_v2": user['ltuid'],
                        "ltoken_v2": user['ltoken'],
                        "cookie_token_v2": user['cookie_token'],
                        "account_id_v2": user['account_id'],
                        "account_mid_v2": user['account_mid'],
                        "ltmid_v2": user['ltmid'],
                    }

                    # get the client
                    client = genshin.Client(debug=True)
                    client.set_cookies(cookies)
                    client.default_game = genshin.Game.GENSHIN

                     # get the daily check-in
                    signed_in, claimed_rewards = await client.get_reward_info()
                    if signed_in:
                        pass

                    try:
                        reward = await client.claim_daily_reward()
                    except genshin.InvalidCookies:
                        print("Invalid cookies.")
                    except genshin.GeetestTriggered:
                        print("Geetest triggered on daily reward.")
                    except genshin.AlreadyClaimed:
                        await self.bot.get_user(user['user_id']).send("You have already claimed your daily reward!")
                    else:
                        embedVar = disnake.Embed(
                            title="Your daily reward has been claimed!",
                            colour=config.Success(),
                            timestamp=datetime.datetime.now()
                        )
                        embedVar.add_field(
                            name="<:block_star:1225801267893370961> Reward", value=f"> {reward.name}", inline=True)
                        embedVar.add_field(
                            name="<:block_star:1225801267893370961> Amount", value=f"> {reward.amount}x", inline=True)
                        embedVar.set_footer(
                            text=f"Genshin Impact Indonesia Helper\nBot Version: {config.version}", icon_url=config.icon_url_front)
                        embedVar.set_thumbnail(
                            url=reward.icon
                        )

                        await self.bot.get_user(user['user_id']).send(embed=embedVar)

    @daily_task.before_loop
    async def before_printer_rewards(self):
        print('Waiting to start daily task...')
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(task_daily(bot))
