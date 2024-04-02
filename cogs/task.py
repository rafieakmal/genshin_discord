from disnake.ext import tasks, commands

import time, genshin, config

class task(commands.Cog):
    def __init__(self, bot):
        self.index = 0
        self.bot = bot
        self.claim_rewards.start()

    def cog_unload(self):
        self.claim_rewards.cancel()
    
    @tasks.loop(seconds=1.0)
    async def claim_rewards(self):
        # get the current time with timezones
        now = time.time()
        
        # format the time
        current_time = time.strftime('%H:%M:%S', time.localtime(now))

        # if the unix time is 03:00:00
        if current_time == '03:00:00':
            # get the genshin impact client
            client = genshin.Client()
            cookies = client.login_with_password(email=config.email, password=config.password)

            try:
                reward = await client.claim_daily_reward()
            except genshin.AlreadyClaimed:
                # send a message to the user
                try:
                    await self.bot.get_user(212534595445456897).send(f"Daily reward already claimed")
                except Exception as e:
                    print(f'Error sending message: {e}')
                    pass
            else:
                # send a message to the user
                try:
                    await self.bot.get_user(212534595445456897).send(f"Claimed the daily reward, Claimed {reward.amount}x {reward.name}")
                except Exception as e:
                    print(f'Error sending message: {e}')
                    pass
            
        try:
            if self.index == 0:
                await self.bot.get_user(212534595445456897).send(f"Current Time: {current_time}")

            self.index += 1
            
            # else edit the message
            await self.bot.get_user(212534595445456897).edit(f"Current Time: {current_time}")
        except Exception as e:
            print(f'Error sending message: {e}')
            pass


    @claim_rewards.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(task(bot))