import discord
from discord.ext import commands, tasks
import asyncio
import datetime
from datetime import datetime, timezone
import yt_dlp
import os
import google.generativeai as genai
from dotenv import load_dotenv

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

###  Chatbot Command
@bot.command()
async def chat(ctx, *, message):
    """Chat with the AI"""
    try:
        response = model.generate_content(message)
        await ctx.send(response.text)
    except Exception as e:
        await ctx.send(f"Error: {e}")

###  Reminders
@bot.command()
async def remind(ctx, minutes: int, *, reminder):
    """Set a reminder"""
    remind_time = datetime.now(timezone.utc) + datetime.timedelta(minutes=minutes)
    reminders[ctx.author.id] = (remind_time, reminder)
    await ctx.send(f"Reminder set for {minutes} minutes.")

@bot.command()
async def myreminders(ctx):
    """List user reminders"""
    user_reminders = [f"{r[1]} at {r[0]}" for uid, r in reminders.items() if uid == ctx.author.id]
    await ctx.send("\n".join(user_reminders) if user_reminders else "No reminders set.")

@bot.command()
async def delreminder(ctx):
    """Delete user's reminders"""
    if ctx.author.id in reminders:
        del reminders[ctx.author.id]
        await ctx.send("Reminder deleted.")
    else:
        await ctx.send("No reminders found.")

@tasks.loop(minutes=1)
async def cleanup_reminders():
    """Auto-delete expired reminders"""
    now = datetime.now(timezone.utc)
    expired = [uid for uid, r in reminders.items() if r[0] < now]
    for uid in expired:
        user = bot.get_user(uid)
        if user:
            await user.send(f"Reminder: {reminders[uid][1]}")
        del reminders[uid]

###  Polls
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

###  Summarization
@bot.command()
async def summarize(ctx, *, text):
    """Summarize long text using AI"""
    try:
        response = model.generate_content(f"Summarize this: {text}")
        await ctx.send(response.text)
    except Exception as e:
        await ctx.send(f"Error: {e}")

###  Music Player
@bot.command()
async def play(ctx, url):
    """Play music from YouTube"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await channel.connect()
        ydl_opts = {'format': 'bestaudio'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            url2 = info['url']
        vc = ctx.voice_client
        vc.stop()
        vc.play(discord.FFmpegPCMAudio(url2))
        await ctx.send(f"🎵 Playing {info['title']}")
    else:
        await ctx.send("Join a voice channel first!")

@bot.command()
async def stop(ctx):
    """Stop music"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Stopped music.")
    else:
        await ctx.send("Bot is not in a voice channel.")

###  Welcome Message
@bot.event
async def on_member_join(member):
    """Send a welcome message when a new member joins"""
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if channel:
        await channel.send(f"Welcome {member.mention} to {member.guild.name}! 🎉")

###  Start Bot
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    cleanup_reminders.start()

async def main():
    async with bot:
        await bot.start(DISCORD_TOKEN)

asyncio.run(main())