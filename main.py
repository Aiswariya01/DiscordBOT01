import discord
from discord.ext import commands, tasks
import asyncio
import datetime
from datetime import datetime, timezone, timedelta
import yt_dlp
import os
import google.generativeai as genai
from dotenv import load_dotenv
from collections import deque

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Intents & Bot Initialization
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Store reminders
reminders = {}
# Music Queue
music_queue = deque()

### Startup Message
@bot.event
async def on_ready():
    print(f"✅ Bot is online as {bot.user}")
    cleanup_reminders.start()
    for guild in bot.guilds:
        for channel in guild.text_channels:
            await channel.send("🤖 Bot is now online and ready to assist! 🚀")
            break

### Chat Command
@bot.command()
async def chat(ctx, *, message):
    """Chat with the AI"""
    try:
        response = model.generate_content(message)
        await ctx.send(response.text)
    except Exception as e:
        await ctx.send(f"Error: {e}")

### Reminders
@bot.command()
async def remind(ctx, minutes: int, *, reminder):
    """Set a reminder"""
    remind_time = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    reminders[(ctx.author.id, ctx.channel.id)] = (remind_time, reminder)
    await ctx.send(f"⏳ Reminder set for {minutes} minutes.")

@tasks.loop(minutes=1)
async def cleanup_reminders():
    """Auto-delete expired reminders"""
    now = datetime.now(timezone.utc)
    expired = [(uid, cid) for (uid, cid), r in reminders.items() if r[0] < now]
    for uid, cid in expired:
        channel = bot.get_channel(cid)
        if channel:
            await channel.send(f"🔔 Reminder: {reminders[(uid, cid)][1]}")
        del reminders[(uid, cid)]

### Polls
@bot.command()
async def poll(ctx, question, *options):
    """Create a poll"""
    if len(options) < 2:
        await ctx.send("You must provide at least two options.")
        return
    poll_message = f"📊 **{question}**\n" + "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(options)])
    message = await ctx.send(poll_message)
    reactions = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
    for i in range(len(options)):
        await message.add_reaction(reactions[i])

### Summarization
@bot.command()
async def summarize(ctx, *, text):
    """Summarize long text using AI"""
    try:
        response = model.generate_content(f"Summarize this: {text}")
        await ctx.send(response.text)
    except Exception as e:
        await ctx.send(f"Error: {e}")

### Music System
@bot.command()
async def play(ctx, url):
    """Play music from YouTube"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
        ydl_opts = {'format': 'bestaudio', 'noplaylist': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']
        music_queue.append((url2, info['title']))
        await ctx.send(f"🎵 Added to queue: {info['title']}")
        if not ctx.voice_client.is_playing():
            await play_next(ctx)
    else:
        await ctx.send("Join a voice channel first!")

async def play_next(ctx):
    if music_queue:
        url, title = music_queue.popleft()
        ctx.voice_client.stop()
        ctx.voice_client.play(discord.FFmpegPCMAudio(url), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(ctx), bot.loop))
        await ctx.send(f"🎵 Now playing: {title}")

@bot.command()
async def stop(ctx):
    """Stop music"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        music_queue.clear()
        await ctx.send("Stopped music and cleared queue.")

### Custom Welcome Message
@bot.event
async def on_member_join(member):
    """Send a welcome message when a new member joins"""
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"Welcome {member.mention} to {member.guild.name}! 🎉")

### Start Bot
async def main():
    async with bot:
        await bot.start(DISCORD_TOKEN)

asyncio.run(main())
