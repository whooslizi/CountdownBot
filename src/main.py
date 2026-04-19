import discord
from discord.ext import commands, tasks
import datetime
import pytz
import os
import json
import random
from dotenv import load_dotenv

# Load secrets
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
USER_ID = int(os.getenv('USER_ID'))

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='?', intents=intents)

DATA_FILE = "data.json"

QUOTES = [
    "Success is not final, failure is not fatal: it is the courage to continue that counts.",
    "Believe you can and you're halfway there.",
    "The only way to do great work is to love what you do.",
    "It always seems impossible until it's done.",
    "Don't watch the clock; do what it does. Keep going.",
    "The future depends on what you do today.",
    "Hardships often prepare ordinary people for an extraordinary destiny.",
    "Action is the foundational key to all success.",
    "Your talent determines what you can do. Your motivation determines how much you are willing to do.",
    "Small steps in the right direction can turn out to be the biggest steps of your life."
]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    data = load_data()
    
    if not data:
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send(f"<@{USER_ID}> Setup required. Please use: ?set_test YYYY-MM-DD HH:MM Timezone")
    else:
        if not announce_days_left.is_running():
            announce_days_left.start()

@bot.command()
async def set_test(ctx, date_str: str, time_str: str, tz_str: str):
    """Usage: ?set_test 2026-06-15 09:00 Asia/Ho_Chi_Minh"""
    try:
        # Validate format and timezone
        test_date = f"{date_str} {time_str}"
        pytz.timezone(tz_str)
        
        data = {
            "test_date": test_date,
            "timezone": tz_str
        }
        save_data(data)
        
        await ctx.send(f"Success. Test date set to {test_date} ({tz_str}). Daily countdown initialized.")
        
        if not announce_days_left.is_running():
            announce_days_left.start()
            
    except Exception as e:
        await ctx.send(f"Error: {e}. Use format: YYYY-MM-DD HH:MM Region/City")

@tasks.loop(hours=24)
async def announce_days_left():
    data = load_data()
    if not data:
        return

    channel = bot.get_channel(CHANNEL_ID)
    if not channel:
        return

    tz = pytz.timezone(data['timezone'])
    test_dt = tz.localize(datetime.datetime.strptime(data['test_date'], '%Y-%m-%d %H:%M'))
    
    now = datetime.datetime.now(tz)
    delta = test_dt - now
    days_left = delta.days + 1
    
    quote = random.choice(QUOTES)

    if days_left < 0:
        await channel.send(f"<@{USER_ID}> The test date has passed. {quote}")
        announce_days_left.stop()
    elif days_left == 0:
        await channel.send(f"<@{USER_ID}> Today is the day. {quote}")
    else:
        await channel.send(f"<@{USER_ID}> {days_left} days left until your test. {quote}")

bot.run(TOKEN)
