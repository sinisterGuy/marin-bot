import asyncio
import discord
from discord.ext import commands
#import validators
#from validators import ValidationFailure
import yt_dlp as youtube_dl
import os
import time
from datetime import datetime, timedelta
import browser_cookie3

class CookieManager:
  def __init__(self, cookie_file='cookies.txt'):
      self.cookie_file = cookie_file
      self.last_refresh = None
      
  def get_valid_cookies(self):
      """Get cookies if they're fresh, otherwise refresh"""
      if not self._cookies_need_refresh():
          return True
          
      try:
          # Get cookies from Chrome (change to 'firefox' if needed)
          cookies = browser_cookie3.chrome(domain_name='youtube.com')
          
          # Write in Netscape format
          with open(self.cookie_file, 'w') as f:
              f.write("# Netscape HTTP Cookie File\n")
              for cookie in cookies:
                  if 'youtube' in cookie.domain:
                      f.write(
                          f"{cookie.domain}\t"
                          f{"TRUE" if cookie.subdomain else "FALSE"}\t"
                          f{cookie.path}\t"
                          f{"TRUE" if cookie.secure else "FALSE"}\t"
                          f{int(cookie.expires or time.time() + 3600)}\t"
                          f{cookie.name}\t"
                          f{cookie.value}\n"
                      )
          self.last_refresh = datetime.now()
          return True
      except Exception as e:
          print(f"Cookie refresh failed: {e}")
          return False
          
  def _cookies_need_refresh(self):
      """Check if cookies are older than 6 hours"""
      if not os.path.exists(self.cookie_file):
          return True
          
      if self.last_refresh is None:
          file_time = datetime.fromtimestamp(os.path.getmtime(self.cookie_file))
          return (datetime.now() - file_time) > timedelta(hours=6)
          
      return (datetime.now() - self.last_refresh) > timedelta(hours=6)

class music_cog(commands.Cog):
  def __init__(self, client):
    self.client = client
    self.cookie_manager = CookieManager()
    
    #all the music related stuff
    self.is_playing = False

    # 2d array containing [song, channel]
    self.music_queue = []
    # self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    # self.YDL_OPTIONS = {
    #     'format': 'bestaudio/best',
    #     'cookiefile': 'cookies.txt',
    #     'noplaylist': True,
    #     'quiet': True,
    #     'no_warnings': True,
    #     'default_search': 'ytsearch',
    #     'source_address': '0.0.0.0',  # IPv4 fallback
    #     'force_ipv4': True,
    #     'geo_bypass': True,
    #     'extractor_retries': 3,
    #     'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36','Accept-Language': 'en-US,en;q=0.9'},
    #     'extract_flat': False,  # Ensure full extraction
    #     'force_generic_extractor': False,  # Use specific extractor
    #     'socket_timeout': 10,
    #     'extractor_args': {'youtube': {'skip': ['dash', 'hls'],'player_client': ['android']}}
    # }
    self.YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'cookiefile': 'cookies.txt',
    'mark_watched': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0',
    'force_ipv4': True,
    'geo_bypass': True,
    'extractor_retries': 3,
    'socket_timeout': 15,
    'http_headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    },
    'extractor_args': {
        'youtube': {
            'skip': ['dash', 'hls'],
            'player_client': ['android_creator'],
            'player_skip': ['configs'],
            'max_comments': [0]  # Disable comments extraction
        }
    },
    'postprocessor_args': {
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192'
    }
}
    # self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    self.FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -thread_queue_size 1024',
    'options': '-vn -b:a 128k -filter:a "volume=0.8" -af "apad=pad_dur=2"',
    }

    #self.vc = ""

  def format_duration(self, duration):
    """Format duration (in seconds) into MM:SS format."""
    minutes, seconds = divmod(duration, 60)
    return f"{minutes}:{seconds:02}"
    
  '''
  def is_url(self, url_string: str) -> bool:
    result = validators.url(url_string)

    if isinstance(result, ValidationFailure):
      return False

    return result
  '''

  # def search_yt(self, item):
  #   with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
  #     try: 
  #       info = ydl.extract_info("ytsearch:%s" % item, download=False)['entries'][0]
  #     except Exception as e:
  #       print(f"Error extracting info: {e}")
  #       return False

  #   #await ctx.send(info['url'])
  #   print(f"Audio source URL: {info['formats'][0]['url']}")  # Debug statement
  #   return {'source': info['formats'][0]['url'], 'title': info['title']}

  async def refresh_cookies(self):
    """Automatically refresh cookies if they expire"""
    try:
        # This requires your deployment to have browser available
        import subprocess
        subprocess.run([
            'yt-dlp',
            '--cookies-from-browser', 'chrome',
            '--print', 'cookie_header',
            'https://www.youtube.com'
        ], check=True, stdout=open('cookies.txt', 'w'))
        print("Cookies refreshed successfully")
    except Exception as e:
        print(f"Couldn't refresh cookies: {e}")

  async def search_yt(self, item):
    # Ensure fresh cookies
    if not self.cookie_manager.get_valid_cookies():
      print("Warning: Using fallback without cookies")
    with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
        try:
            #info = ydl.extract_info(f"ytsearch:{item}", download=False)
            def sync_search():
              with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
                try:
                    return ydl.extract_info(f"ytsearch:{item}", download=False)
                except youtube_dl.utils.DownloadError as e:
                    # Try fallback method if cookies fail
                    if "Sign in to confirm" in str(e):
                        print("Cookie auth failed, trying fallback...")
                        temp_options = self.YDL_OPTIONS.copy()
                        temp_options.pop('cookiefile', None)
                        return youtube_dl.YoutubeDL(temp_options).extract_info(f"ytsearch:{item}", download=False)
            info = await asyncio.to_thread(sync_search) 
            print(f"Info dictionary: {info}")  # Debug statement
            if 'entries' in info:
                info = info['entries'][0]
            else:
                return False

            if 'url' not in info:
                print("No URL found in info dictionary")
                return False

            # Extract metadata
            title = info.get('title', 'Unknown Title')
            artist = info.get('uploader', 'Unknown Artist')
            duration = info.get('duration', 0)  # Duration in seconds
            thumbnail = info.get('thumbnail', '')  # Thumbnail URL

            return {
                'source': info['url'],
                'title': title,
                'artist': artist,
                'duration': duration,
                'thumbnail': thumbnail,
            }

            #return {'source': info['url'], 'title': info['title']}
        except Exception as e:
            print(f"Error extracting info: {e}")
            return False

  async def send_now_playing(self, ctx, song):
    """Send an embed message for the currently playing song."""
    embed = discord.Embed(
        title="🎶 Now Playing",
        description=f"**Title:** {song['title']}\n**Artist:** {song['artist']}\n**Duration:** {self.format_duration(song['duration'])}",
        color=0x00ff00,
    )
    if song['thumbnail']:
        embed.set_thumbnail(url=song['thumbnail'])
    await ctx.send(embed=embed)

  async def play_next(self, ctx, error=None):
    if error:
      print(f"Player error: {error}")
    #vc=ctx.voice_client
    if len(self.music_queue) > 0:
      self.is_playing = True

      #get the first url
      song = self.music_queue[0][0]
      m_url = self.music_queue[0][0]['source']

      #remove the first element as you are currently playing it
      self.music_queue.pop(0)

      # Send "Now Playing" message
      asyncio.run_coroutine_threadsafe(self.send_now_playing(ctx, song), self.client.loop)

      vc=ctx.voice_client

      #vc.play(discord.FFmpegOpusAudio(m_url, **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
      #await ctx.send('Playing your song now!')
      # Create audio source with error handling
      def create_source():
          try:
              return discord.FFmpegOpusAudio(
                  m_url,
                  **self.FFMPEG_OPTIONS
              )
          except Exception as e:
              print(f"Error creating audio source: {e}")
              raise
      
      source = await asyncio.to_thread(create_source)

      # Play with proper error handling
      vc.play(source,after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx, e),self.client.loop))

    else:
      self.is_playing = False

  async def play_music(self, ctx):
    vc=ctx.voice_client
    if len(self.music_queue) > 0:
      self.is_playing = True
      song = self.music_queue[0][0]  # Define the song variable
      m_url = self.music_queue[0][0]['source']

      # Debug: Print the audio source URL
      print(f"Audio source URL: {m_url}")

      # Display song info
      await self.send_now_playing(ctx, song)
            
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

  @commands.command(aliases=["q"], help="Shows the current music queue")
  async def queue(self, ctx):
      if len(self.music_queue) == 0:
          await ctx.send("The queue is empty!")
          return

      # Create an embed for the queue
      embed = discord.Embed(
          title="🎶 Music Queue",
          description=f"**{len(self.music_queue)} songs in queue**",
          color=0x00ff00,
      )

      # Add each song to the embed
      for i, song_info in enumerate(self.music_queue):
          song = song_info[0]
          embed.add_field(
              name=f"{i + 1}. {song['title']}",
              value=f"**Artist:** {song['artist']}\n**Duration:** {self.format_duration(song['duration'])}",
              inline=False,
          )

      await ctx.send(embed=embed)

  @commands.command()
  async def test(self, ctx):
      await ctx.send("Cog is working!")

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
    # Refresh cookies if needed
    if not self.cookie_manager.get_valid_cookies():
      await ctx.send("⚠ Cookie refresh failed, trying fallback method...")
    # Initial loading message
    msg = await ctx.send("🔍 Searching... (This may take a moment)")
    # First try with cookies
    song = await self.search_yt(query)
    
    # If failed due to auth, try once without cookies
    if not song and "Sign in to confirm" in str(e):
        await ctx.send("⚠ Retrying without cookies...")
        temp_options = self.YDL_OPTIONS.copy()
        temp_options.pop('cookiefile', None)
        song = await self.search_yt(query)

    if not song:
        return await msg.edit(content="❌ Couldn't find that song. Try a different query.")

    embed=discord.Embed(title="", description="Audio is currectly downloading this may take a minute\nGetting everything ready, playing audio soon...", color=0xffffff)
    embed.set_footer(text="Ohm Audio", icon_url="https://media.discordapp.net/attachments/847649142834593803/881308944159617104/Ohm.png")
    await ctx.send(embed=embed)
    song = await self.search_yt(query) #async call
    if type(song) == type(True):
      error=discord.Embed(title="Error", description="Could not download the song.\nIncorrect format try another keyword.\nThis could be due to playlist or a livestream format.", color=0xFF0000)
      error.set_footer(text="Ohm Audio", icon_url="https://media.discordapp.net/attachments/847649142834593803/881308944159617104/Ohm.png")
      await ctx.send(embed=error)
    else:
              
      #await ctx.send("Song added to the queue")
      #await ctx.send("Please be patient")
      # Display song info
      embed = discord.Embed(
          title="🎶 Song Added to Queue",
          description=f"**Title:** {song['title']}\n**Artist:** {song['artist']}\n**Duration:** {self.format_duration(song['duration'])}",
          color=0x00ff00,
      )
      if song['thumbnail']:
          embed.set_thumbnail(url=song['thumbnail'])
      await ctx.send(embed=embed)
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

async def setup(client):
  await client.add_cog(music_cog(client))
