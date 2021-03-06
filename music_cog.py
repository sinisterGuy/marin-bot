import discord
from discord.ext import commands
#import validators
#from validators import ValidationFailure
import youtube_dl

class music_cog(commands.Cog):
  def __init__(self, client):
    self.client = client
    
    #all the music related stuff
    self.is_playing = False

    # 2d array containing [song, channel]
    self.music_queue = []
    self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

    #self.vc = ""

  '''
  def is_url(self, url_string: str) -> bool:
    result = validators.url(url_string)

    if isinstance(result, ValidationFailure):
      return False

    return result
  '''

  def search_yt(self, item):
    with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
      try: 
        info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
      except Exception: 
        return False

    #await ctx.send(info['url'])
    return {'source': info['formats'][0]['url'], 'title': info['title']}

  def play_next(self, ctx):
    vc=ctx.voice_client
    if len(self.music_queue) > 0:
      self.is_playing = True

      #get the first url
      m_url = self.music_queue[0][0]['source']

      #remove the first element as you are currently playing it
      self.music_queue.pop(0)

      vc.play(discord.FFmpegOpusAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
      #await ctx.send('Playing your song now!')
    else:
      self.is_playing = False

  async def play_music(self, ctx):
    vc=ctx.voice_client
    if len(self.music_queue) > 0:
      self.is_playing = True

      m_url = self.music_queue[0][0]['source']
            
      #try to connect to voice channel if you are not already connected

      if vc == "" or vc == None:
        vc = await self.music_queue[0][1].connect()
      else:
        await vc.move_to(self.music_queue[0][1])
            
      print(self.music_queue)
      #remove the first element as you are currently playing it
      self.music_queue.pop(0)

      vc.play(discord.FFmpegOpusAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
    else:
      self.is_playing = False

  @commands.command()
  async def join(self, ctx):
    if ctx.author.voice is None:
      await ctx.send('Baka! Join a voice channel first!')
      return
    voice_channel = ctx.message.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    else:
      await ctx.voice_client.move_to(voice_channel)
    await ctx.send('IGI: I\'m going in')

  @commands.command()
  async def leave(self, ctx):
    if ctx.voice_client is None:
      await ctx.send('Baka! I am not in a voice channel!')
    else:
      await ctx.guild.voice_client.disconnect()
      await ctx.send('Okay, waise bhi khas maza nhi aya.')

  """
  @commands.command()
  async def play(self, ctx):
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

    msg = ctx.message.content
    song = msg.split(" ",1)[1]
    #print(song)
    #await ctx.send(song)

    if (self.is_url(song)):
      url=song
      with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
        vc.play(source)
    else:
      if(self.search_yt(song)):
        url=self.music_queue[0][0]['source']
        vc.play(discord.FFmpegOpusAudio.from_probe(url, **FFMPEG_OPTIONS))

    '''
    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
      info = ydl.extract_info(url, download=False)
      url2 = info['formats'][0]['url']
      source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
      vc.play(source)
    '''
    await ctx.send('Playing your song now.')
    """
  @commands.command(aliases=["p"], help="Plays a selected song from youtube")
  async def play(self, ctx, *args):
    query = " ".join(args)
    if ctx.author.voice is None:
      await ctx.send('Baka! Join a voice channel first!')
      return
    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
      await voice_channel.connect()
    embed=discord.Embed(title="", description="Audio is currectly downloading this may take a minute\nGetting everything ready, playing audio soon...", color=0xffffff)
    embed.set_footer(text="Ohm Audio", icon_url="https://media.discordapp.net/attachments/847649142834593803/881308944159617104/Ohm.png")
    await ctx.send(embed=embed)
    song = self.search_yt(query)
    if type(song) == type(True):
      error=discord.Embed(title="Error", description="Could not download the song.\nIncorrect format try another keyword.\nThis could be due to playlist or a livestream format.", color=0xFF0000)
      error.set_footer(text="Ohm Audio", icon_url="https://media.discordapp.net/attachments/847649142834593803/881308944159617104/Ohm.png")
      await ctx.send(embed=error)
    else:
              
      await ctx.send("Song added to the queue")
      #await ctx.send("Please be patient")
      self.music_queue.append([song, voice_channel])
                
      if self.is_playing == False:
        await self.play_music(ctx)

  @commands.command()
  async def pause(self, ctx):
    if ctx.voice_client.is_playing():
      ctx.voice_client.pause()
      await ctx.send('Audio paused!')
    else:
      await ctx.send('Baka! I didn\'t even play anything!')

  @commands.command()
  async def resume(self, ctx):
    if ctx.voice_client.is_paused():
      ctx.voice_client.resume()
      await ctx.send('Audio resumed!')
    else:
      await ctx.send('Baka! I didn\'t even pause anything!')

  @commands.command()
  async def stop(self, ctx):
    if ctx.voice_client is None:
      await ctx.send('Baka! I am not in a voice channel!')
    else:
      ctx.guild.voice_client.stop()
      await ctx.send('Ye red light area hai!')

def setup(client):
  client.add_cog(music_cog(client))
