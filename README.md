# prawbot
Python bot that gets post updates from reddit and posts in discord guild at a defined interval

**Requirements to run this program**

Python version 3.8.2
Packages to install: praw, asyncio, discord, dotenv

**Files to modify**

Praw.ini - You must first create a reddit application [here](https://www.reddit.com/prefs/apps) before filling out this file.
.env - You must first create a reddit bot [here](https://discordapp.com/developers/applications) before filling out this file.
prawbot.py - Use the header from Praw.ini that you set for instantiating the reddit instance and also your username for the user_agent