import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta
import os  # Import the os module to access environment variables
from flask import Flask
from threading import Thread

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Dictionary to store series information
series_info = {
    'HDWLK': {
        'name': 'How Did We Get Here Lee Ji-Kyung',
        'role_id': 1228968453986324581,
        'url': 'https://flexscans.com/manga/how-did-we-get-here-lee-ji-kyung/xx'
    },
    'OMA': {
        'name': 'Office Menace Alert',
        'role_id': 1231220871805538456,
        'url': 'https://flexscans.com/manga/office-menace-alert/xx'
    },
    'PGBM': {
        'name': 'Playing a Game with my Busty Manager',
        'role_id': 1228968582445269133,
        'url': 'https://flexscans.com/manga/playing-a-game-with-my-busty-manager/xx'
    },
    'THS': {
        'name': 'The High Society',
        'role_id': 1228968673352355930,
        'url': 'https://flexscans.com/manga/the-high-society/xx'
    }
}

vip_channel_id = 1228948429019811940  # Replace with your VIP channel ID
late_channel_id = 1228948547827925104  # Replace with your "10 mins late" channel ID
time_remaining_channel_id = 1247835352941596742  # Replace with your time remaining channel ID
all_series_role_id = 1228965477670457364
vip_role_id = 1228969150039457833  # Replace with your VIP role ID

ongoing_notifications = []

@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')
    update_time_remaining.start()

@bot.command()
async def notify(ctx, series_abbr: str, chapter_number: int, duration: int):
    series = series_info.get(series_abbr.upper())
    if not series:
        await ctx.send("Series not found.")
        return

    # Send message to VIP channel
    vip_message = f"**{series['name']}** chapter **{chapter_number}** has been released for <@&{vip_role_id}>."
    vip_channel = bot.get_channel(vip_channel_id)
    await vip_channel.send(vip_message)

    release_time = datetime.utcnow() + timedelta(hours=duration)
    ongoing_notifications.append((series_abbr.upper(), chapter_number, release_time))

    await ctx.send(f"Notification scheduled for {series['name']} chapter {chapter_number}.")

@tasks.loop(minutes=1)
async def update_time_remaining():
    now = datetime.utcnow()
    new_ongoing_notifications = []

    time_remaining_channel = bot.get_channel(time_remaining_channel_id)
    await time_remaining_channel.purge()

    for series_abbr, chapter_number, release_time in ongoing_notifications:
        series = series_info[series_abbr]
        if now >= release_time:
            late_channel = bot.get_channel(late_channel_id)
            late_message = (
                f"<@&{all_series_role_id}> <@&{series['role_id']}>\n"
                f"**{series['name']}** chapter **{chapter_number}** has been released!\n"
                f"{series['url'].replace('xx', str(chapter_number))}"
            )
            await late_channel.send(late_message)
        else:
            new_ongoing_notifications.append((series_abbr, chapter_number, release_time))
            remaining_time = release_time - now
            hours, remainder = divmod(int(remaining_time.total_seconds()), 3600)
            minutes = remainder // 60
            time_remaining_message = (
                f"**{series['name']}** chapter **{chapter_number}** releases in "
                f"{hours}h {minutes}m"
            )
            await time_remaining_channel.send(time_remaining_message)

    ongoing_notifications[:] = new_ongoing_notifications

# Flask app to keep the Glitch project alive
app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run():
    app.run(host='0.0.0.0', port=9000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Call keep_alive to start the Flask app
keep_alive()

# Run the bot with your token from the environment variable
bot_token = os.getenv('BOT_TOKEN')
bot.run(bot_token)
