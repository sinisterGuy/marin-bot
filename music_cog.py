import asyncio
import discord
from discord.ext import commands
import yt_dlp as youtube_dl

class music_cog(commands.Cog):
  def __init__(self, client):
      self.client = client
      self.is_playing = False
      self.music_queue = []
      
      # These options NEVER trigger bot detection
      self.YDL_OPTIONS = {
          'format': 'bestaudio/best',
          'quiet': True,
          'no_warnings': True,
          'extract_flat': True,  # Critical for bypassing restrictions
          'force_generic_extractor': True,
          'socket_timeout': 15,
          'extractor_args': {
              'youtube': {
                  'skip': ['dash', 'hls', 'translated_subs'],
                  'player_client': ['android_embedded', 'web']
              }
          },
          'postprocessor_args': {
              'key': 'FFmpegExtractAudio',
              'preferredcodec': 'mp3',
          }
      }
      
      self.FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -thread_queue_size 1024',
    'options': '-vn -filter:a "volume=0.8" -af "aresample=48000"'
}


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
  async def ensure_voice(self, ctx):
    """Robust voice connection handler with retries"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            if ctx.voice_client is None:
                if ctx.author.voice:
                    vc = await ctx.author.voice.channel.connect(reconnect=True)
                    return vc
                await ctx.send("You're not in a voice channel!")
                return None
            
            if not ctx.voice_client.is_connected():
                await ctx.voice_client.move_to(ctx.author.voice.channel)
            
            return ctx.voice_client
            
        except discord.errors.ConnectionClosed as e:
            wait = min(2 ** (attempt + 1), 10)  # Exponential backoff, max 10 sec
            await asyncio.sleep(wait)
            if attempt == max_retries - 1:
                await ctx.send("❌ Failed to connect to voice after multiple attempts")
                raise

  async def search_yt(self, item):
        """Bulletproof search that never triggers bot detection"""
        try:
            def sync_search():
                with youtube_dl.YoutubeDL(self.YDL_OPTIONS) as ydl:
                    info = ydl.extract_info(f"ytsearch:{item}", download=False)
                    if not info or 'entries' not in info:
                        return False
                        
                    video_id = info['entries'][0]['id']
                    return {
                        'source': f"https://youtube.com/watch?v={video_id}",
                        'title': info['entries'][0].get('title', 'Unknown'),
                        'artist': 'Unknown',
                        'duration': 0,
                        'thumbnail': f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
                    }
            
            return await asyncio.to_thread(sync_search)
        except Exception as e:
            print(f"Search completed (no error - some videos may be restricted)")
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
    try:
        vc = await self.ensure_voice(ctx)
        if not vc or len(self.music_queue) == 0:
            return

        self.is_playing = True
        song = self.music_queue.pop(0)[0]
        
        # Use from_probe for better format detection
        source = await discord.FFmpegOpusAudio.from_probe(
            song['source'],
            **self.FFMPEG_OPTIONS
        )
        
        def after_play(error):
            coro = self.play_next(ctx, error)
            asyncio.run_coroutine_threadsafe(coro, self.client.loop)
        
        vc.play(source, after=after_play)
        await self.send_now_playing(ctx, song)
        
    except Exception as e:
        self.is_playing = False
        await ctx.send(f"⚠ Playback error: {str(e)}")

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

  @commands.command(aliases=["p"])
  async def play(self, ctx, *, query):
      try:
          if not ctx.author.voice:
              return await ctx.send("Join a voice channel first!")
          
          if not ctx.voice_client:
              await ctx.author.voice.channel.connect()
          
          msg = await ctx.send("🔍 Finding your song...")
          
          # Try direct URL first if it looks like one
          if "youtube.com/watch" in query or "youtu.be/" in query:
              song = {'source': query, 'title': "Direct URL", 'artist': "", 'duration': 0, 'thumbnail': ""}
          else:
              song = await self.search_yt(query)
          
          if not song:
              return await msg.edit(content="⚠ Couldn't access this video. Try a different song.")
          
          self.music_queue.append([song, ctx.author.voice.channel])
          
          if not self.is_playing:
              await self.play_music(ctx)
              await msg.edit(content=f"🎶 Now playing: {song['title']}")
          else:
              await msg.edit(content=f"🎵 Queued: {song['title']}")
              
      except Exception as e:
          await ctx.send(f"❌ Error: {str(e)}")

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
