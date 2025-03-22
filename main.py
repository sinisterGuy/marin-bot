import asyncio
import os
import signal
import discord
from discord.ext import commands
from discord.utils import find
import requests
import json
import random
from replit import db
from keep_alive import keep_alive
from music_cog import setup
from discord.ext.commands import BucketType
#from datetime import datetime
#import threading

# Kill previous instances of the bot
try:
    # Get the current process ID
    current_pid = os.getpid()

    # Find all Python processes
    pids = [int(pid) for pid in os.popen("pgrep -f python").read().splitlines()]

    # Kill all Python processes except the current one
    for pid in pids:
        if pid != current_pid:
            os.kill(pid, signal.SIGTERM)
except Exception as e:
    print(f"Error killing previous instances: {e}")

if not os.path.exists("/home/runner/.apt/usr/bin/ffmpeg"):
  os.system("apt-get update")
  os.system("apt-get install -y ffmpeg")

client = commands.Bot(command_prefix = '~', intents = discord.Intents.all())

# Add a delay before restarting
async def restart_bot():
  retry_delay = 60  # Start with 60 seconds
  while True:
      print(f"Rate limited. Waiting for {retry_delay} seconds before retrying...")
      await asyncio.sleep(retry_delay)
      try:
          print("Restarting bot...")
          new_client = commands.Bot(command_prefix='~', intents=discord.Intents.all())
          await new_client.start(os.environ['Huehuehue'])
          break  # Exit the loop if restart is successful
      except discord.errors.HTTPException as e:
          if e.status == 429:
              retry_delay *= 2  # Double the delay for exponential backoff
              if retry_delay > 600:  # Cap the delay at 10 minutes
                  retry_delay = 600
          else:
              raise e

# async def setup(client):
#   await client.add_cog(music_cog(client))

# # Add a cooldown to the play command
# @commands.cooldown(1, 5, BucketType.user)  # Allow 1 command per 5 seconds per user
# @client.command()
# async def play(ctx, *args):
#     try:
#         # Your play command logic
#         await ctx.send("Playing song...")
#     except discord.errors.HTTPException as e:
#         if e.status == 429:  # Rate limit error
#             retry_after = e.response.headers.get('Retry-After')  # Get the retry delay
#             await asyncio.sleep(float(retry_after))  # Wait for the specified delay
#             await ctx.send("Retrying after rate limit...")

async def load_cogs():
  await setup(client)

bad_words = ["gandu", "fuck", "bitch", "whore", "bokachoda", "banchod", "madarchod", "bc", "mc", "bantu", "randy", "dick", "fucking", "bastard", "bloody hell", "gudmarani", "chutiya", "asshole", "bhenchod", "fucker", "shit", "bullshit", "sala", "harami", "chodna", "lund", "chut", "gand", "bal", "baal", "khanki", "rendi", "dhur mara", "bara"]

starter_advices = ["You shouldn't abuse like this!", "Drink some water", "Are chill dude...hota hai", "Itna ghussa mat ho", "Itni gaali kyu de rha hai?", "Enough! Don't use such bad words.", "Baba maa ghore ei sikhiyeche?", "Stop abusing you sussy baka!", "Why are you cursing, my friend?"]

sayonara = ["bye", "byee", "goodbye", "tata", "cya", "see you later"]


if "respond" not in db.keys():
  db["respond"] = True

def get_quote():
  try:
      response = requests.get("https://animechan.vercel.app/api/random")
      response.raise_for_status()  # Raise an error for bad status codes
      return response.json()
  except requests.exceptions.RequestException as e:
      print(f"Error fetching quote: {e}")
      return {"error": "Could not fetch quote."}

def get_joke():
  response=requests.get("https://official-joke-api.appspot.com/random_joke")
  json_data = json.loads(response.text)
  joke = json_data
  return(joke)

def get_value():
  response=requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
  json_data = json.loads(response.text)
  value = json_data
  return(value)

def get_news():
  response=requests.get("https://newsapi.org/v2/top-headlines?country=in&apiKey=API_KEY")
  json_data = json.loads(response.text)
  news = json_data
  return(news)

def get_covid():
  response=requests.get("https://covid-19-data.p.rapidapi.com/country/code")
  json_data = json.loads(response.text)
  covid = json_data
  return(covid)

def update_animelist(new_anime):
  if "animes" in db.keys():
    animes = db["animes"]
    animes.append(new_anime)
    db["animes"] = animes
  else:
    db["animes"] = [new_anime]

def delete_animelist(index):
  animes = db["animes"]
  if len(animes) > index:
    del animes[index]
  db["animes"] = animes

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  await load_cogs()

@client.event
async def on_guild_join(guild):
    general = find(lambda x: x.name == 'general',  guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send('I\'m back bitches!')

@client.event
async def on_message(message):
  await client.process_commands(message)
  if message.author == client.user:
    return
  
  msg = message.content

  '''
  if msg.startswith('~'):
    embed=discord.Embed(title="", description="Bot temporarily disabled for maintenance!\nSome features may not work!", color=0xffffff)
    await message.channel.send(embed=embed)
  '''

  if msg.startswith('~help'):
    await message.channel.send('General:\n~hello - Bot gives a gentle reply\n~mention n - Pings everyone n times\n~clear n - Clears n above messages\n~panu - You should refrain yourself from trying this\n~quote - Gives a random anime quote\n~joke - Tells a random internet joke\n~news - "This feature is yet to be developed"\n\nAnime: (Some features are not fully developed yet)\n~anime - Recommends a random anime from its DB\n~addanime - Add your fav anime on the list\n~delanime - Deletes the mentioned anime\n~listanime - Gives the full list of animes in its DB\n\nProfanity:\n~respond - Turn it on or off as per your choice\n\nMusic: (The commands here are self-explanatory)\n~join\n~leave\n~play\n~pause\n~resume\n~stop\n\nMore features coming next year! Stay tuned!')

  if msg.startswith('~hello'):
    await message.channel.send('world')

  if msg.startswith('~panu'):
    await message.channel.send('You need help, my friend.')
  
  if msg.startswith('~quote'):
    quote = get_quote()
    await message.channel.send(quote.get("quote", "Could not fetch quote."))

  if msg.startswith('~joke'):
    joke = get_joke()
    await message.channel.send(f"{joke.get('setup', 'Could not fetch joke.')}\n{joke.get('punchline', '')}")
    await message.channel.send('\n\nStill not as big of a joke as my creator\'s life!')

  if msg.startswith('~value'):
    value = get_value()
    await message.channel.send(value)

  if msg.startswith('~news'):
    news = get_news()
    await message.channel.send(news)

  if msg.startswith('~covid'):
    covid = get_covid()
    await message.channel.send(covid)

  options = []
  if "animes" in db.keys():
    options = db["animes"]

  if msg.startswith('~anime'):
    await message.channel.send(random.choice(options))

  if db["respond"]:
    if any(word in msg for word in bad_words):
      await message.channel.send(random.choice(starter_advices))

    if any(word in msg for word in sayonara):
      await message.channel.send('Get lost dear')

  if msg.startswith('~addanime'):
    anime = msg.split('~addanime ',1)[1]
    update_animelist(anime)
    await message.channel.send('Wakatta Senpai')

  if msg.startswith('~delanime'):
    animes = []
    if "animes" in db.keys():
      index = int(msg.split("~delanime",1)[1])
      delete_animelist(index)
      animes = db[animes]
    await message.channel.send(animes)

  if msg.startswith('~listanime'):
    animes = []
    if "animes" in db.keys():
      animes = db["animes"]
    await message.channel.send(animes)

  if msg.startswith('~respond'):
    value = msg.split("~respond ",1)[1]
  
    if value.lower() == 'on':
      db["respond"] = True
      await message.channel.send("Responding feature is on!")
    else:
      db["respond"] = False
      await message.channel.send("Responding feature is off!")

@client.command(pass_context=True)
async def mention(ctx):
  msg = ctx.message.content
  number = int(msg.split("~mention",1)[1])
  channel = discord.utils.get(ctx.guild.text_channels, name="announcements")
  count = 0
  for i in range(number):
    if channel:
      await channel.send(f'Huehuehue {ctx.message.guild.default_role}')
      count+=1
    else:
      await ctx.send(f'Huehuehue {ctx.message.guild.default_role}')
      count+=1
    if count>=420:
      await channel.purge(limit=420)
      await ctx.send('420 messages have been purged💀')
      count-=420

@client.command(pass_context=True)
async def clear(ctx, amount=69):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f'{amount} messages have been purged💀')

"""
async def checkTime(ctx):
    # This function runs periodically every 1 second
    threading.Timer(1, checkTime).start()

    now = datetime.now()

    current_time = now.strftime("%H:%M:%S")

    channel = discord.utils.get(ctx.guild.text_channels, name="announcements")
    if channel:
      if(current_time == '02:05:00'):  # check if matches with the desired time
        await channel.send(f'Huehuehue {ctx.message.guild.default_role}')
"""

keep_alive()
# client.run(os.environ['Huehuehue'])
# Run the bot
try:
    client.run(os.environ['Huehuehue'])
except discord.errors.HTTPException as e:
    if e.status == 429:  # Rate limit error
        print("Rate limited. Waiting before retrying...")
        asyncio.run(restart_bot())