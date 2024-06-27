from disnake.ext import tasks, commands
import time, genshin, config, disnake, datetime
from database.database import Database
import aiohttp, asyncio, random, base64

# create a database object
client_db = Database()

class task_claim_codes(commands.Cog):
    def __init__(self, bot):
        """
        Initialize the task
        """
        self.bot = bot
        if self.claim_codes.is_running():
            self.claim_codes.cancel()
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
        cookies = await self.get_user_cookies(user=kwargs['user'])
        client = await self.get_genshin_client(cookies=cookies)
        await self.process_redeem_codes(user=kwargs['user'], client=client)

    async def get_user_cookies(self, **account) -> dict:
        """
        Get the user cookies
        """
        return {
            "ltuid_v2": account['user']['ltuid_v2'],
            "ltoken_v2": account['user']['ltoken_v2'],
            "cookie_token_v2": account['user']['cookie_token_v2'],
            "account_id_v2": account['user']['account_id_v2'],
            "account_mid_v2": account['user']['account_mid_v2'],
            "ltmid_v2": account['user']['ltmid_v2'],
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
            try:
                all_claimed_codes = [claimed_code['code'] async for claimed_code in client_db.find('users_claimed_code', {'user_id': kwargs['user']['user_id']})]
                all_claimed_codes_set = set(all_claimed_codes)
                filtered_redeem_codes = [redeem_code['code'] for redeem_code in redeem_codes if redeem_code['code'] not in all_claimed_codes_set]

                if filtered_redeem_codes:
                    for redeem_code in filtered_redeem_codes:
                        await self.attempt_redeem_code(user=kwargs['user'], client=kwargs['client'], redeem_code=redeem_code)
            except Exception as e:
                print(f"Error processing redeem codes: {e}")

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
            await self.refresh_invalid_cookies(user=kwargs['user'])
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
                    {k: getattr(cookies, k) for k in ["cookie_token_v2", "account_mid_v2", "account_id_v2", "ltoken_v2", "ltmid_v2", "ltuid_v2"]}
                )
                print(
                    f"Refreshed cookies for user {kwargs['user']['user_id']}")
            else:
                print(
                    f"Failed to refresh cookies for user {kwargs['user']['user_id']}")
        except Exception as e:
            print(
                f"Error refreshing cookies for user in task claim codes {kwargs['user']['user_id']}: {e}")

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

