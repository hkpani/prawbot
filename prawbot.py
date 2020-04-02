# Python version 3.8.2
# prawbot.py
# Author: hkpani
# Version: 1.0
# Description: This is a bot that schedules updates to be formatted as discord messages
# in your guild. The interval, subreddit, and query can be changed with the bot commands
# As of version 1.0 this bot only supports getting posts in the format title : URL/image 
# to your discord guild
import os 

import praw
import asyncio
import time 
import discord
from dotenv import load_dotenv
from discord.ext import commands

user_agent = "Getting game updates by /u/<insert reddit username>"
r = praw.Reddit('<insert header from praw.ini>', user_agent=user_agent)

#######global variables#########
sub_name = "gaming" #r/gaming as default
post_time = 3600 #1 hour default
game_title = "animal crossing" 
sched_event = None
################################

#this method loads variables defined in .env file of the same directory
#User must define their DISCORD_TOKEN for the bot and DISCORD_GUILD name 
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
bot = commands.Bot(command_prefix = '$')
guild = None #this will be set later in on_ready()

client = discord.Client()

#The method to actually GET data from the subreddit and query that is set
#This is called in the background task time_passed every post_time interval
#The relevant subreddit data will be posted in the general channel of the guild
async def subreddit_search(): 
	global game_title
	subreddit = r.subreddit(sub_name)
	guild = discord.utils.find(lambda x: x.name == GUILD , bot.guilds)
	channel = discord.utils.get(guild.channels,name='general')
	for x in subreddit.search(query=game_title,sort="top", time_filter="day", limit=5): #search returns submissions listinggenerator
		await channel.send('{}: {}'.format(x.title,x.url))

#The background task is instantiated in on_ready and reinstantiated if the user uses the GNtime command
async def time_passed(): #this is the main task for the news updates
	await bot.wait_until_ready()
	while not bot.is_closed():
		await asyncio.sleep(post_time)
		await subreddit_search()

#on_ready command outputs a message to the general channel and instantiates the time_passed background task
@bot.event
async def on_ready():
	global sched_event
	guild = discord.utils.find(lambda x: x.name == GUILD , bot.guilds)
	channel = discord.utils.get(guild.channels,name='general')
	sched_event = bot.loop.create_task(time_passed())
	await channel.send('GNbot is up and ready')

@bot.command(name='GNtitle',help='This command will update the game posts reported from reddit ex: GNtitle animal crossing')
async def change_game_title(ctx,*args):
	global game_title
	media_name = ''
	for x in args:
		media_name += x + ' '

	game_title = media_name #update the global variable game_title
	await ctx.send('New game title set: {}'.format(media_name))

@bot.command(name='GNtime',help='This command will update the frequency of posts from reddit, input in hours ex: GNtime 3. Note this will cancel the currently scheduled post')
async def post_interval(ctx,hours):
	global sched_event
	global post_time
	post_time = int(float(hours) * 60 * 60)#convert to seconds as that will be the units for the task
	 #cancel the current background task, task will run with the new post_time
	sched_event.cancel()
	sched_event = bot.loop.create_task(time_passed())
	await ctx.send('New interval set: {} hours'.format(hours))

@bot.command(name='GNsub', help='This command will update the subreddit being used for retrieving posts. If subreddit does not exist, then prints a message to the channel, ex: GNsub gaming')
async def change_subreddit(ctx,sub):
	global sub_name
	try:
		r.subreddits.search_by_name(sub, exact=True)
	except:
		await ctx.send('Invalid subreddit entered, try again')
	else:
		sub_name = sub
		await ctx.send('New subreddit set: {}'.format(sub))

if __name__ == "__main__":
	bot.run(TOKEN)