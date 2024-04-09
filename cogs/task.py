from disnake.ext import tasks, commands
import time, genshin, config, disnake, datetime
from database.database import Database

# create a database object
client_db = Database()
print('Connected to the database')

class task(commands.Cog):
    def __init__(self, bot):
        self.index = 0
        self.bot = bot
        self.message_id = 0
        self.claim_rewards.start()

    def cog_unload(self):
        self.claim_rewards.cancel()
    
    @tasks.loop(seconds=1.0)
    async def claim_rewards(self):
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

        # print(f'Current Thread Running: {current_time} | {date} | {day} | {month} | {year} | {day_raw} | {month_raw} | {year_raw}')

        # if day raw equals to 1 and 16
        if day_raw in ('01', '16'):
            # time must be 03:00:00
            if current_time == '03:00:00':
                # get members in the role of the guild id=1051526111135272990
                guild = self.bot.get_guild(config.guild)
                
                # get the role
                role = disnake.utils.get(guild.roles, name='Abyss Master')

                member_ids = [member.id for member in guild.members if member.roles and role in member.roles]
                
                # reset the role
                if member_ids:
                    for member_id in member_ids:
                        member = guild.get_member(member_id)
                        await member.remove_roles(role)
                    
                    # delete all users from the database
                    client_db.delete_many('users_claimed', {})
                    
                    # get the channel
                    channel = self.bot.get_channel(config.broadcast_channel)
                    
                    # send the message
                    message_builder = "**Morning Travelers!**"
                    message_builder += "\n\nToday is the day of the Abyss reset!"
                    message_builder += "\nI have removed the Abyss Master role from all members who had it before"
                    message_builder += "\n\nGood luck on your floor clears and I hope you get 36 <:abyss_stars:1225579783660765195>!"
                    message_builder += "\nRemember, travelers! The time has come to reclaim your rightful place as the Abyss Master. Use the command ``/reqabyssmaster``"
                    message_builder += "\nin the <#1065702573971091477> channel and let your power be known!"

                    embedVar = disnake.Embed(
                        title="Abyss Reset Notification",
                        description=message_builder,
                        colour=config.Success(),
                        timestamp=datetime.datetime.now()
                    )
                    embedVar.set_footer(text=f"Genshin Impact Indonesia Helper\nBot Version: {config.version}")
                    embedVar.set_image(url=config.abyss_header)

                    await channel.send(embed=embedVar)
                else:
                    client_db.delete_many('users_claimed', {})

                    channel = self.bot.get_channel(config.broadcast_channel)
                    
                    message_builder = "**Morning Travelers!**"
                    message_builder += "\n\nToday is the day of the Abyss reset!"
                    message_builder += "\nI have removed the Abyss Master role from all members who had it before"
                    message_builder += "\n\nGood luck on your floor clears and I hope you get 36 <:abyss_stars:1225579783660765195>!"
                    message_builder += "\nRemember, travelers! The time has come to reclaim your rightful place as the Abyss Master. Use the command ``/reqabyssmaster``"
                    message_builder += "\nin the <#1065702573971091477> channel and let your power be known!"

                    embedVar = disnake.Embed(
                        title="Abyss Reset Notification",
                        description=message_builder,
                        colour=config.Success(),
                        timestamp=datetime.datetime.now()
                    )
                    embedVar.set_footer(text=f"Genshin Impact Indonesia Helper\nBot Version: {config.version}")
                    embedVar.set_image(url=config.abyss_header)

                    await channel.send(embed=embedVar)
        else:
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

                        print(cookies)

                        # get the client
                        client = genshin.Client(debug=True)
                        client.set_cookies(cookies)
                        client.default_game = genshin.Game.GENSHIN

                        print(client)

                        # get the daily check-in

                        signed_in, claimed_rewards = await client.get_reward_info()

                        print(signed_in, claimed_rewards)

                        if signed_in:
                            pass
                        else:
                            try:
                                reward = await client.claim_daily_reward()
                            except genshin.InvalidCookies:
                                print("Invalid cookies.")
                            except genshin.GeetestTriggered:
                                print("Geetest triggered on daily reward.")
                            except genshin.AlreadyClaimed:
                                await self.bot.get_user(user['user_id']).send("You have already claimed your daily reward!")
                            else:
                                await self.bot.get_user(user['user_id']).send(f"Your daily reward has been claimed! {reward.amount} {reward.name} has been added to your account!")
            


        

    @claim_rewards.before_loop
    async def before_printer(self):
        print('waiting...')
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(task(bot))