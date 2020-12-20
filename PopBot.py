import discord
import arrow
import requests
import aiohttp
from discord.ext import commands, tasks

# -----------------------------------------------------
#-------------------- START CONFIG --------------------
# -----------------------------------------------------

discordBotToken = ""
battleMetricsServerID = None

# -----------------------------------------------------
#--------------------- END CONFIG ---------------------
# -----------------------------------------------------

intents = discord.Intents()
client = commands.Bot(command_prefix="-",intents=intents)
client.remove_command('help')


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        pass

@client.event
async def on_ready():
    print(f"[{arrow.now().format('YYYY-MM-DD HH:mm:ss')}] Bot successfully started\n")
    change_status.start()

@tasks.loop(seconds=60)
async def change_status():
    serverData = await makeWebRequest(f"https://api.battlemetrics.com/servers/{battleMetricsServerID}")
    if serverData == None:
        return

    serverPlayers = serverData['data']['attributes']['players']
    serverMaxPlayers = serverData['data']['attributes']['maxPlayers']
    serverQueue = serverData['data']['attributes']['details']['rust_queued_players']

    if serverQueue > 0:
        await client.change_presence(activity=discord.Game(f"{serverPlayers}/{serverMaxPlayers} Queue {serverQueue}"))
    else:
        await client.change_presence(activity=discord.Game(f"{serverPlayers}/{serverMaxPlayers}"))

async def makeWebRequest(URL):
    async with aiohttp.ClientSession() as session:
        async with session.get(URL) as preJSData:
            if preJSData.status == 200:
                return await preJSData.json()
            else:
                print(f"BattleMetrics Error [Code {preJSData.status}]")

client.run(discordBotToken)