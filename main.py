import os
import discord
from discord.ext import commands
from discord.utils import find
import requests
import json
import random
from replit import db
from keep_alive import keep_alive
import youtube_dl
#from datetime import datetime
#import threading

client = commands.Bot(command_prefix = '~', intents = discord.Intents.all())

bad_words = ["gandu", "fuck", "bitch", "whore", "bokachoda", "banchod", "madarchod", "bc", "mc", "bantu", "randy", "dick", "fucking", "bastard", "bloody hell", "gudmarani", "chutiya", "asshole", "bhenchod", "fucker", "shit", "bullshit", "sala", "harami", "chodna", "lund", "chut", "gand", "bal", "baal", "khanki", "rendi", "dhur mara", "bara"]

starter_advices = ["You shouldn't abuse like this!", "Drink some water", "Are chill dude...hota hai", "Itna ghussa mat ho", "Itni gaali kyu de rha hai?", "Enough! Don't use such bad words.", "Baba maa ghore ei sikhiyeche?", "Stop abusing you sussy baka!", "Why are you cursing, my friend?"]

sayonara = ["bye", "byee", "goodbye", "tata", "cya", "see you later"]


if "respond" not in db.keys():
  db["respond"] = True

def get_quote():
  response=requests.get("https://animechan.vercel.app/api/random")
  json_data = json.loads(response.text)
  quote = json_data
  return(quote)

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

  if msg.startswith('~help'):
    await message.channel.send('General:\n~hello - Bot gives a gentle reply\n~panu - You should refrain yourself from trying this\n~quote - Gives a random anime quote\n~joke - Tells a random internet joke\n~news - "This feature is yet to be developed"\n\nAnime: (Some features are not fully developed yet)\n~anime - Recommends a random anime from its DB\n~addanime - Add your fav anime on the list\n~delanime - Deletes the mentioned anime\n~listanime - Gives the full list of animes in its DB\n\nProfanity:\n~respond - Turn it on or off as per your choice\n\nMusic: (The commands here are self-explanatory)\n~join\n~leave\n~play\n~pause\n~resume\n~stop\n\nMore features coming next year! Stay tuned!')

  if msg.startswith('~hello'):
    await message.channel.send('world')

  if msg.startswith('~panu'):
    await message.channel.send('You need help, my friend.')
  
  if msg.startswith('~quote'):
    quote = get_quote()
    await message.channel.send(quote)

  if msg.startswith('~joke'):
    joke = get_joke()
    await message.channel.send(joke)
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
async def join(ctx):
    if ctx.author.voice is None:
      await ctx.send('Baka! Join a voice channel first!')
      return
    voice_channel = ctx.message.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      await ctx.voice_client.move_to(voice_channel)
    await ctx.send('IGI: I\'m going in')

@client.command(pass_context=True)
async def leave(ctx):
  if ctx.voice_client is None:
    await ctx.send('Baka! I am not in a voice channel!')
  else:
    await ctx.guild.voice_client.disconnect()
    await ctx.send('Okay, waise bhi khas maza nhi aya.')

@client.command(pass_context=True)
async def play(ctx,url):
  if ctx.author.voice is None:
    await ctx.send('Baka! Join a voice channel first!')
    return
  voice_channel = ctx.message.author.voice.channel
  if ctx.voice_client is None:
    await voice_channel.connect()
  ctx.guild.voice_client.stop()
  FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
  YDL_OPTIONS = {'format': 'bestaudio'}
  vc = ctx.voice_client

  with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
    info = ydl.extract_info(url, download=False)
    url2 = info['formats'][0]['url']
    source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
    vc.play(source)
  await ctx.send('Playing your song now.')

@client.command(pass_context=True)
async def pause(ctx):
  if ctx.voice_client.is_playing():
    ctx.voice_client.pause()
    await ctx.send('Audio paused!')
  else:
    await ctx.send('Baka! I didn\'t even play anything!')

@client.command(pass_context=True)
async def resume(ctx):
  if ctx.voice_client.is_paused():
    ctx.voice_client.resume()
    await ctx.send('Audio resumed!')
  else:
    await ctx.send('Baka! I didn\'t even pause anything!')

@client.command(pass_context=True)
async def stop(ctx):
  if ctx.voice_client is None:
    await ctx.send('Baka! I am not in a voice channel!')
  else:
    ctx.guild.voice_client.stop()
    await ctx.send('Ye red light area hai!')

@client.command(pass_context=True)
async def mention(ctx):
  msg = ctx.message.content
  number = int(msg.split("~mention",1)[1])
  channel = discord.utils.get(ctx.guild.text_channels, name="announcements")
  for i in range(number):
    if channel:
      await channel.send(f'Huehuehue {ctx.message.guild.default_role}')
    else:
      await ctx.send(f'Huehuehue {ctx.message.guild.default_role}')

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
client.run(os.environ['Huehuehue'])