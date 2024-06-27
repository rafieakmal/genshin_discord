from disnake.ext import tasks, commands
import time, genshin, config, disnake, datetime
from database.database import Database
import asyncio
import base64
import random

# create a database object
client_db = Database()

class task_daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if self.daily_task.is_running():
            self.daily_task.cancel()
        self.daily_task.start()

    def cog_unload(self):
        self.daily_task.cancel()

    @tasks.loop(time=datetime.time(hour=23, minute=0, second=1, tzinfo=datetime.timezone(datetime.timedelta(hours=7))))
    async def daily_task(self):
        """
        Run the daily task
        """
        users = await client_db.find('users', {})  # Added callback=None to satisfy the required argument
        if not users:
            return

        for user in users:
            cookies = await self.get_user_cookies(user=user)

            client = await self.get_genshin_client(cookies=cookies, debug=True)
            client.default_game = genshin.Game.GENSHIN

            try:
                signed_in, _ = await client.get_reward_info()
                if not signed_in:
                    reward = await client.claim_daily_reward()
                    await self.notify_user_reward_claimed(user=user, reward=reward)
            except genshin.InvalidCookies:
                await self.refresh_invalid_cookies(user=user)
            except genshin.GeetestTriggered:
                print("Geetest triggered on daily reward.")
            except genshin.AlreadyClaimed:
                await self.notify_user_already_claimed(user=user)

    async def notify_user_reward_claimed(self, **kwargs):
        """
        Notify the user that the daily reward has been claimed
        """
        embedVar = disnake.Embed(
            title="Your daily reward has been claimed!",
            colour=config.Success(),
            timestamp=datetime.datetime.now()
        )
        embedVar.add_field(name="<:block_star:1225801267893370961> Reward", value=f"> {kwargs['reward'].name}", inline=True)
        embedVar.add_field(name="<:block_star:1225801267893370961> Amount", value=f"> {kwargs['reward'].amount}x", inline=True)
        embedVar.set_footer(text=f"Genshin Impact Indonesia Helper\nBot Version: {config.version}", icon_url=config.icon_url_front)
        embedVar.set_thumbnail(url=kwargs['reward'].icon)

        return await self.bot.get_user(kwargs['user']['user_id']).send(embed=embedVar)

    async def notify_invalid_cookies(self, **kwargs):
        """
        Notify the user that the cookies are invalid
        """
        await client_db.delete_one('users', {'user_id': kwargs['user']['user_id']})

        embedVar = disnake.Embed(
            title="Dear user",
            colour=config.Error(),
            timestamp=datetime.datetime.now()
        )
        embedVar.add_field(
            name="<:block_star:1225801267893370961> Message",
            value="> We apologize, but you have been logged out due to invalid cookies. Please log in again. We do not save any of your private information for your safety and privacy. Thank you",
            inline=False
        )
        embedVar.set_footer(
            text=f"Genshin Impact Indonesia Helper\nBot Version: {config.version}", icon_url=config.icon_url_front)

        return await self.bot.get_user(kwargs['user']['user_id']).send(embed=embedVar)
    
    async def refresh_invalid_cookies(self, **kwargs):
        """
        Refresh invalid cookies by logging in again and updating the database.
        """
        user_account = await self.get_user_account(**kwargs)
        email = user_account['email']
        password = user_account['password']
        
        try:
            client = genshin.Client()
            port_randomize = random.randint(5000, 9000)
            cookies = await client.os_login_with_password(email, password, port=port_randomize)

            if cookies:
                # Update the database with the new cookies
                await client_db.update_one(
                    'users',
                    {'user_id': kwargs['user']['user_id']},
                    {"$set": {k: getattr(cookies, k) for k in [
                        "cookie_token_v2", "account_mid_v2", "account_id_v2", "ltoken_v2", "ltmid_v2", "ltuid_v2"]}}
                )
                print(f"Refreshed cookies for user {kwargs['user']['user_id']}")
            else:
                print(f"Failed to refresh cookies for user {kwargs['user']['user_id']}")
        except Exception as e:
            print(f"Error refreshing cookies for user {kwargs['user']['user_id']}: {e}")
    
    async def notify_user_already_claimed(self, **kwargs):
        """
        Notify the user that the daily reward has already been claimed
        """
        return await self.bot.get_user(kwargs['user']['user_id']).send("You have already claimed your daily reward!")
    
    async def get_user_cookies(self, **kwargs):
        """
        Get the user cookies
        """
        return {
            "ltuid_v2": kwargs['user']['ltuid_v2'],
            "ltoken_v2": kwargs['user']['ltoken_v2'],
            "cookie_token_v2": kwargs['user']['cookie_token_v2'],
            "account_id_v2": kwargs['user']['account_id_v2'],
            "account_mid_v2": kwargs['user']['account_mid_v2'],
            "ltmid_v2": kwargs['user']['ltmid_v2'],
        }

    async def get_user_account(self, **kwargs):
        """
        Get the user account and decode the password
        """
        password_decoded_bytes = kwargs['user']['password'].encode("ascii")
        password_decoded = base64.b64decode(password_decoded_bytes)
        password_decoded = password_decoded.decode("ascii")

        return {
            "email": kwargs['user']['email'],
            "password": password_decoded
        }

    async def get_genshin_client(self, **kwargs):
        """
        Get the genshin client
        """
        return genshin.Client(**kwargs)

    @daily_task.before_loop
    async def before_printer_rewards(self):
        print('Waiting to start daily task...')
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(task_daily(bot))
