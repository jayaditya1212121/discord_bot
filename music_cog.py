from ast import alias
import discord
from discord.ext import commands
#youtube_dl not working use this
import yt_dlp


class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # music related stuff
        self.is_playing = False
        self.is_paused = False

        # 2d array containing [song, channel]
        self.music_queue = []
        self.YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist': 'True', }
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                               'options': '-vn'}

        self.vc = None

    # searching the item on youtube
    def search_yt(self, item):
        with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{item}", download=False)
                #print(info)
                # dict containing all details of video too big just use first element of entries
            except Exception:
                return False

        return {'source': info['entries'][0]['url'], 'title': info['entries'][0]['title']}

    async def play_next(self):
        if len(self.music_queue) > 0:
            self.is_playing = True

            # get the first url
            m_url = self.music_queue[0][0]['source']

            # remove the first element as you are currently playing it
            self.music_queue.pop(0)

            audio = discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS)
            self.vc.play(audio, after=lambda e: self.play_next())
        else:
            self.is_playing = False


    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.is_playing = True

            m_url = self.music_queue[0][0]['source']
            #await ctx.send("got here 3")

            # try to connect to voice channel if you are not already connected
            if self.vc == None or not self.vc.is_connected():
                #await ctx.send('get in if?')
                self.vc = await self.music_queue[0][1].connect()
                #await ctx.send('get in if? 2')
                print(self.vc)
                #discord voice client object

                # in case we fail to connect
                if self.vc == None:
                    await ctx.send("Could not connect to the voice channel")
                    return
            else:
                #await ctx.send('get in else?')
                #move voice client to which ever voice channel user is in
                await self.vc.move_to(self.music_queue[0][1])

            # remove the first element as you are currently playing it
            self.music_queue.pop(0)

            audio = discord.FFmpegPCMAudio(m_url, **self.FFMPEG_OPTIONS)
            #await ctx.send("got here 4")
            self.vc.play(audio, after=lambda e: self.play_next())
            #await ctx.send("got here 5")
        else:
            self.is_playing = False

    @commands.command(name="play", aliases=["p", "playing"], help="Plays a selected song from youtube")
    async def play(self, ctx, *args):
        query = " ".join(args)

        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            # you need to be connected so that the bot knows where to go
            await ctx.send("Connect to a voice channel!")
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if type(song) == type(True):
                await ctx.send(
                    "Could not download the song. Incorrect format try another keyword. This could be due to playlist or a livestream format.")
            else:
                await ctx.send("Song added to the queue")
                self.music_queue.append([song, voice_channel])
                #await ctx.send("got here 1")

                if self.is_playing == False:
                    #await ctx.send("got here 2")
                    await self.play_music(ctx)

    @commands.command(name="pause", help="Pauses the current song being played")
    async def pause(self, ctx, *args):
        if self.is_playing:
            self.is_playing = False
            self.is_paused = True
            self.vc.pause()
        elif self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="resume", aliases=["r"], help="Resumes playing with the discord bot")
    async def resume(self, ctx, *args):
        if self.is_paused:
            self.is_paused = False
            self.is_playing = True
            self.vc.resume()

    @commands.command(name="skip", aliases=["s"], help="Skips the current song being played")
    async def skip(self, ctx):
        if self.vc != None and self.vc:
            self.vc.stop()
            # try to play next in the queue if it exists
            await self.play_music(ctx)

    @commands.command(name="queue", aliases=["q"], help="Displays the current songs in queue")
    async def queue(self, ctx):
        q = ""
        for i in range(0, len(self.music_queue)):

            q += self.music_queue[i][0]['title'] + "\n"

        if q != "":
            await ctx.send(q)
        else:
            await ctx.send("No music in queue")

    @commands.command(name="clear", aliases=["c", "bin"], help="Stops the music and clears the queue")
    async def clear(self, ctx):
        if self.vc != None and self.is_playing:
            self.vc.stop()
        self.music_queue = []
        await ctx.send("Music queue cleared")

    @commands.command(name="leave", aliases=["disconnect", "l", "d"], help="Kick the bot from VC")
    async def dc(self, ctx):
        self.is_playing = False
        self.is_paused = False
        await self.vc.disconnect()