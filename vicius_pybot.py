import nextcord
import os
import re
from dotenv import load_dotenv
from nextcord.ext import commands
from nextcord.shard import EventItem
import wavelinkcord as wavelink

load_dotenv()   
TOKEN = os.getenv("BOT_TOKEN")

intents = nextcord.Intents.all()
client = nextcord.Client()
bot = commands.Bot(command_prefix="!", intents=intents)

URL_REGEX = re.compile(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)+(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

@bot.event
async def on_ready():
    print("Bot ready!")
    bot.loop.create_task(on_node())

async def on_node():
    node: wavelink.Node = wavelink.Node(uri=os.getenv("LAVALINK_URI"), password=os.getenv("LAVALINK_PASS"))
    await wavelink.NodePool.connect(client=bot, nodes=[node])
    wavelink.Player.autoplay = True

@bot.slash_command(guild_ids=[])
async def play(interaction: nextcord.Interaction, search):
    if not URL_REGEX.match(search):
        search = f'ytsearch: {search}'
    query = await wavelink.NodePool.get_node().get_tracks(wavelink.YouTubeTrack, search)

    if not query:
        return await interaction.response.send_message("No se encontro ninguna cancion")

    query = query[0]  
    destination = interaction.user.voice.channel

    if not interaction.guild.voice_client:
        vc: wavelink.Player = await destination.connect(cls=wavelink.Player)
    else:
        vc: wavelink.Player = interaction.guild.voice_client

    if vc.queue.is_empty and not vc.is_playing():
        await vc.play(query)
        await interaction.response.send_message(f"Escuchando: {vc.current.title} - {vc.current.author}")
    else:
        await vc.queue.put_wait(query)
        await interaction.response.send_message(f"Se agrego a la lista: {query.title} - {query.author}")

@bot.slash_command(guild_ids=[])
async def skip(interaction: nextcord.Interaction):
    vc: wavelink.Player = interaction.guild.voice_client
    await vc.stop()

    if vc.queue.is_empty:
        await interaction.response.send_message(f"Se termino la playlist")

@bot.slash_command(guild_ids=[])
async def clear_list(interaction: nextcord.Interaction):
    vc: wavelink.Player = interaction.guild.voice_client

    if not vc.queue.is_empty:
        await vc.queue.clear()
        await interaction.response.send_message(f"Lista de reproducción eliminada")
    else:
        await interaction.response.send_message(f"No hay canciones en la lista de reproducción")

@bot.slash_command(guild_ids=[])
async def song(interaction: nextcord.Interaction):
    vc: wavelink.Player = interaction.guild.voice_client

    if vc.is_playing():
        await interaction.response.send_message(f"Escuchando: {vc.current.title} - {vc.current.author}")
    else:
        await interaction.response.send_message("No hay ninguna cancion reproduciendose")

@bot.slash_command(guild_ids=[])
async def pause(interaction: nextcord.Interaction):
    vc: wavelink.Player = interaction.guild.voice_client
    
    if vc.is_playing():
        await vc.pause()
        await interaction.response.send_message(f"Pausado")
    else:
        await interaction.response.send_message(f"La cancion ya esta pausada")

@bot.slash_command(guild_ids=[])
async def resume(interaction: nextcord.Interaction):
    vc: wavelink.Player = interaction.guild.voice_client
    
    if vc.is_playing():
        await interaction.response.send_message(f"La cancion se esta escuchando")
    else:
        await vc.resume()
        await interaction.response.send_message(f"La cancion se reanudo")

@bot.slash_command(guild_ids=[])
async def disconnect(interaction: nextcord.Interaction):
    vc: wavelink.Player = interaction.guild.voice_client
    await vc.disconnect()
    await interaction.response.send_message(f"Pybot desconectado")

@bot.slash_command(guild_ids=[])
async def queue(interaction: nextcord.Interaction):
    vc: wavelink.Player = interaction.guild.voice_client

    if not vc.queue.is_empty:
        song_counter = 0
        songs = []
        queue = vc.queue.copy()
        embed = nextcord.Embed(title="Lista")

        for song in queue:
            song_counter += 1
            songs.append(song)
            embed.add_field(name=f"[{song_counter}] Duration {song.duration}", value=f"{song.title}", inline=False)

        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("La lista esta vacia")


    

bot.run(TOKEN)