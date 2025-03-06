DiscordBot01
A Discord bot built using Python and discord.py. This bot includes AI chat, music playback, reminders, polls, and more!

Features 
AI Chatbot and Summarize – Chat with an AI-powered assistant and summarize paragraphs using Gemini API.
Reminders – Set reminders.
Polls – Create interactive polls with reactions.
Music Player – Play music from YouTube in a voice channel.
Welcome Messages – Greets new members upon joining.
Auto start Message - Sends a message when the bot goes online

Command	Description
!chat <message>,	Chat with the AI
!remind <minutes> <reminder>,	Set a reminder
!poll <question> <options>,	Create a poll
!summarize <text>,	Get an AI-generated summary
!play <YouTube URL>,	Play music from YouTube and queue songs
!stop,	Stop and disconnect the bot from voice

Dependencies
discord.py (for Discord API interaction)
google-generativeai (for Gemini AI chat & summarization)
yt-dlp (for YouTube audio streaming)
ffmpeg (for audio processing)
python-dotenv (for loading environment variables)

License
This project is licensed under the MIT License.

