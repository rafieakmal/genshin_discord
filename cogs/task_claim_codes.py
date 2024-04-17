from disnake.ext import tasks, commands
import time, genshin, config, disnake, datetime
from database.database import Database
import aiohttp, asyncio

# create a database object
client_db = Database()

class task_claim_codes(commands.Cog):
    def __init__(self, bot):
        """
        Initialize the task
        """
        self.bot = bot
        self.claim_codes.start()

    def cog_unload(self):
        """
        Cancel the task when the cog is unloaded
        """
        self.claim_codes.cancel()
    
    @tasks.loop(seconds=10)
    async def claim_codes(self):
        """
        Get the redeem codes and process them
        """
        users = await client_db.find('users', {})
        if users:
            for user in users:
                await self.process_user(user=user)

    async def process_user(self, **kwargs):
        """
        Get the user cookies and process the redeem codes
        """
        cookies = self.get_user_cookies(user=kwargs['user'])
        client = self.get_genshin_client(cookies=cookies)
        await self.process_redeem_codes(user=kwargs['user'], client=client)

    def get_user_cookies(self, **kwargs):
        """
        Get the user cookies
        """
        return {
            "ltuid_v2": kwargs['user']['ltuid'],
            "ltoken_v2": kwargs['user']['ltoken'],
            "cookie_token_v2": kwargs['user']['cookie_token'],
            "account_id_v2": kwargs['user']['account_id'],
            "account_mid_v2": kwargs['user']['account_mid'],
            "ltmid_v2": kwargs['user']['ltmid'],
        }

    def get_genshin_client(self, **kwargs):
        """
        Get the genshin client
        """
        client = genshin.Client()
        client.set_cookies(kwargs['cookies'])
        client.default_game = genshin.Game.GENSHIN
        return client

    async def process_redeem_codes(self, **kwargs):
        """
        Process the redeem codes
        """
        redeem_codes = await client_db.find('redeem_codes', {})
        if redeem_codes:
            all_redeem_codes = [redeem_code['code'] for redeem_code in redeem_codes]
            all_claimed_codes = [claimed_code['code'] for claimed_code in await client_db.find('users_claimed_code', {'user_id': kwargs['user']['user_id']})]
            filtered_redeem_codes = [code for code in all_redeem_codes if code not in all_claimed_codes]

            if filtered_redeem_codes:
                for redeem_code in filtered_redeem_codes:
                    await self.attempt_redeem_code(user=kwargs['user'], client=kwargs['client'], redeem_code=redeem_code)

    async def attempt_redeem_code(self, **kwargs):
        """
        Attempt to redeem the code
        """
        if await client_db.find_one('users_claimed_code', {'user_id': kwargs['user']['user_id'], 'code': kwargs['redeem_code']}):
            return

        try:
            await asyncio.sleep(1)  # sleep for 1s
            await kwargs['client'].redeem_code(kwargs['redeem_code'])
        except genshin.RedemptionException:
            await self.handle_error_code(user=kwargs['user'], redeem_code=kwargs['redeem_code'])
        except genshin.AccountNotFound:
            await self.notify_account_not_found(user=kwargs['user'])
        except genshin.InvalidCookies:
            await self.notify_invalid_cookies(user=kwargs['user'])
        else:
            await self.notify_user(user=kwargs['user'], redeem_code=kwargs['redeem_code'])

    async def notify_user(self, **kwargs):
        """
        Notify the user that the code has been claimed
        """
        embedVar = disnake.Embed(
            title="Your redeem code has been claimed!",
            colour=config.Success(),
            timestamp=datetime.datetime.now()
        )
        embedVar.add_field(name="<:block_star:1225801267893370961> Code", value=f"> {kwargs['redeem_code']}", inline=True)
        embedVar.set_footer(text=f"Genshin Impact Indonesia Helper\nBot Version: {config.version}", icon_url=config.icon_url_front)

        await client_db.insert_one('users_claimed_code', {'user_id': kwargs['user']['user_id'], 'code': kwargs['redeem_code']})
        await self.bot.get_user(kwargs['user']['user_id']).send(embed=embedVar)

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
        embedVar.set_footer(text=f"Genshin Impact Indonesia Helper\nBot Version: {config.version}", icon_url=config.icon_url_front)

        return await self.bot.get_user(kwargs['user']['user_id']).send(embed=embedVar)

    async def notify_account_not_found(self, **kwargs):
        """
        Notify the user that the account is not found
        """
        await client_db.delete_one('users', {'user_id': kwargs['user']['user_id']})

        embedVar = disnake.Embed(
            title="Dear user",
            colour=config.Error(),
            timestamp=datetime.datetime.now()
        )
        embedVar.add_field(name="<:block_star:1225801267893370961> Message", value="> We apologize, but we cannot find your account. Please ensure that you have the correct account. If you have any questions, please contact our support team. Thank you", inline=False)
        embedVar.set_footer(text=f"Genshin Impact Indonesia Helper\nBot Version: {config.version}", icon_url=config.icon_url_front)

        return await self.bot.get_user(kwargs['user']['user_id']).send(embed=embedVar)
    
    async def handle_error_code(self, **kwargs):
        """
        Handle the error code
        """
        return await client_db.insert_one('users_claimed_code', {'user_id': kwargs['user']['user_id'], 'code': kwargs['redeem_code']})



    @claim_codes.before_loop
    async def before_printer_claim_codes(self) -> None:
        """
        Wait until the bot is ready
        """
        print('Waiting to start getting redeem codes...')
        return await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(task_claim_codes(bot))

