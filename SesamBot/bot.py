import discord
from discord.ext import commands
from discord.utils import get

import random
import os
import youtube_dl
import wolframalpha
import time
from dotenv import load_dotenv

load_dotenv()

w_app_id = os.getenv("WOLFRAM")
w_client = wolframalpha.Client(w_app_id)

client = commands.Bot(command_prefix = ".")

@client.event
async def on_ready():
    print("Sesambot ready")
   
   
@client.command(help = "shows ping")
async def hi(ctx):
    await ctx.send(f"hi {round((client.latency * 1000))}ms")

@client.command(help = "returns your prompt")
async def test(ctx, * , prompt):
    await ctx.send(prompt)

@client.command(help = "sends prompt to wolframalpha and displays TOO MANY results")
async def w(ctx, *, prompt):
    
    res = w_client.query(prompt)

    linklist = []
    
    for pod in res.pods:
        for sub in pod.subpods:
            for e in sub.img:
                #time.sleep(0.5)
                linklist.append(e.src)
    
    while len(linklist) > 5:
        linkstring = ""
        for i in range(5):
            linkstring += linklist.pop(0) + " "
        await ctx.send(linkstring)
    
    linkstringlast = ""
    
    if len(linklist) > 0:
        for e in linklist:
            linkstringlast += e + " "
    
    await ctx.send(linkstringlast)
    
    #await ctx.send(answer.text)
    
@client.command(help = "converts prompt to emoji")
async def emoji(ctx, *, prompt):
    numdict = {"1" : ":one:", ":2:" : ":two:", "3" : ":three:", "4" : ":four:", 
                "5" : ":five:", "6" : ":six:", "7" : ":seven:", 
                "8" : ":eight:", "9" : ":nine:", "0" : ":zero:", 
               "!" : ":exclamation:", "?" : ":question"}
    
    out = ""
    for c in prompt:
        if ord(c) > ord("z") or ord(c) < ord("a"):
            if c in numdict:
                out += numdict[c]
            else:
                out += " "
        else:
            out += ":regional_indicator_" + c + ":"
    await ctx.send(out)
    
    
#Voice

@client.command(pass_context=True, aliases=["j"], help = "joins voice channel of user")
async def join(ctx):
    global voice
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)    
    
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
    
    # disconnects and joins in order to fix a sound bug (have I encountered this bug?)
    await voice.disconnect()
    
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"Connected to {channel}")
    
@client.command(aliases=["l"], help ="leaves voice channel")
async def leave(ctx):
    channel = ctx.message.author.voice.channel
    voice = get(client.voice_clients, guild=ctx.guild)  
    
    if voice and voice.is_connected():
        await voice.disconnect()

@client.command(aliases=["p"], help = "plays music from youtube-url")
async def play(ctx, url):
    song_there = os.path.isfile("audio.mp3")
    try:
        if song_there:
            os.remove("audio.mp3")
    except PermissionError:
        await ctx.send("Music playing pls stop")
        return
    voice = get(client.voice_clients, guild=ctx.guild)
    
    ydl_options = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "outtmpl": "SesamBot\\audio.%(ext)s"
    }
    
    with youtube_dl.YoutubeDL(ydl_options) as ydl:
        print("dling audio...")
        ydl.download([url])
    
    """    
    for file in os.listdir("./SesamBot"):
        if file.endswith(".mp3"):
            name = file
            print(f"Renamed file: {file}")
            os.rename(file, "audio.mp3")
    """
    
    voice.play(discord.FFmpegPCMAudio("SesamBot/audio.mp3"), after=lambda e: print("Audio has finished playing"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.07
    
    #nname = name.rsplit("-", 2)
    await ctx.send(f"Playing audio...")
    print("playing")

client.run(os.getenv("DISCORD"))

