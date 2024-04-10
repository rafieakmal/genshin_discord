from disnake.ext import tasks, commands
import time, genshin, config, disnake, datetime
from database.database import Database
import aiohttp, asyncio

# create a database object
client_db = Database()
print('Connected to the database')

class task_claim_codes(commands.Cog):
    def __init__(self, bot):
        self.index = 0
        self.bot = bot
        self.message_id = 0
        self.claim_codes.start()

    def cog_unload(self):
        self.claim_codes.cancel()
    
    @tasks.loop(seconds=10)
    async def claim_codes(self):
        # get the user
        print('Claiming redeem codes...')
        users = client_db.find('users', {})
        if users:
            for user in users:
                # get the user cookies
                cookies = {
                    "ltuid_v2": user['ltuid'],
                    "ltoken_v2": user['ltoken'],
                    "cookie_token_v2": user['cookie_token'],
                    "account_id_v2": user['account_id'],
                    "account_mid_v2": user['account_mid'],
                    "ltmid_v2": user['ltmid'],
                }

                # get the client
                client = genshin.Client()
                client.set_cookies(cookies)
                client.default_game = genshin.Game.GENSHIN

                # get the redeemable codes
                redeem_codes = client_db.find('redeem_codes', {})
                
                if redeem_codes:
                    all_redeem_codes = [redeem_code['code'] for redeem_code in redeem_codes]
                    all_claimed_codes = [claimed_code['code'] for claimed_code in client_db.find('users_claimed_code', {'user_id': user['user_id']})]
                    filtered_redeem_codes = [code for code in all_redeem_codes if code not in all_claimed_codes]

                    if filtered_redeem_codes:
                        for redeem_code in filtered_redeem_codes:
                            if client_db.find_one('users_claimed_code', {'user_id': user['user_id'], 'code': redeem_code}):
                                continue
                            
                            try:
                                # sleep for 5s
                                await asyncio.sleep(1)
                                code = await client.redeem_code(redeem_code)
                            except genshin.RedemptionException:
                                client_db.insert_one('users_claimed_code', {
                                                     'user_id': user['user_id'], 'code': redeem_code})
                                continue
                            except genshin.AccountNotFound:
                                continue
                            else:
                                # send the message
                                if code is None:
                                    client_db.insert_one('users_claimed_code', {'user_id': user['user_id'], 'code': redeem_code})
                                    continue
                                
                                embedVar = disnake.Embed(
                                    title="Your redeem code has been claimed!",
                                    colour=config.Success(),
                                    timestamp=datetime.datetime.now()
                                )
                                embedVar.add_field(name="<:block_star:1225801267893370961> Code", value=f"> {redeem_code}", inline=True)
                                embedVar.set_footer(text=f"Genshin Impact Indonesia Helper\nBot Version: {config.version}", icon_url=config.icon_url_front)

                                client_db.insert_one('users_claimed_code', {'user_id': user['user_id'], 'code': redeem_code})

                                await self.bot.get_user(user['user_id']).send(embed=embedVar)
                    else:
                        continue
    
    @claim_codes.before_loop
    async def before_printer_claim_codes(self):
        print('Waiting to start getting redeem codes...')
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(task_claim_codes(bot))
