from flask import Flask, request
import logging
import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from threading import Thread

load_dotenv()

# Define intents
intents = discord.Intents.default()
if hasattr(intents, 'message_content'):
    intents.message_content = True
else:
    print("The current version of discord.py does not support 'message_content' intent. Please update to discord.py 2.0 or higher.")

# Create bot instance
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

# Channel and role IDs
vip_channel_id = 1228948429019811940
late_channel_id = 1228948547827925104
time_remaining_channel_id = 1247835352941596742
all_series_role_id = 1228965477670457364
vip_role_id = 1228969150039457833

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
    
    # Purge old messages if we have the manage_messages permission
    try:
        await time_remaining_channel.purge()
    except discord.Forbidden:
        print("Bot lacks permission to manage messages in the time remaining channel.")

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
app = Flask(__name__)

@app.route('/')
def home():
    app.logger.info('Home endpoint accessed.')
    return "I'm alive"

def run():
    app.run(host='0.0.0.0', port=8081)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Call keep_alive to start the Flask app
keep_alive()

# Run the bot with your token from the environment variable
bot.run(os.getenv('BOT_TOKEN'))
