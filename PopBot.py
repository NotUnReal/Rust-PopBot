from discord import Intents, Game
from aiohttp import ClientSession
from discord.ext import commands, tasks

# -----------------------------------------------------
#-------------------- START CONFIG --------------------
# -----------------------------------------------------

discordBotToken = "" #type: str
battleMetricsServerID = None #type: int

# -----------------------------------------------------
#--------------------- END CONFIG ---------------------
# -----------------------------------------------------

client = commands.Bot(command_prefix="-",intents=Intents().default(),help_command=None)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        pass

@client.event
async def on_ready():
    print(f"Bot successfully started\n")

@tasks.loop(seconds=60)
async def change_status():

    await client.wait_until_ready()

    serverData = await makeWebRequest(f"https://api.battlemetrics.com/servers/{battleMetricsServerID}")
    if serverData == None:
        return

    serverPlayers = serverData['data']['attributes']['players']
    serverMaxPlayers = serverData['data']['attributes']['maxPlayers']
    serverQueue = serverData['data']['attributes']['details']['rust_queued_players']

    if serverQueue > 0:
        await client.change_presence(activity=Game(f"{serverPlayers}/{serverMaxPlayers} Queue {serverQueue}"))
    else:
        await client.change_presence(activity=Game(f"{serverPlayers}/{serverMaxPlayers}"))

async def makeWebRequest(URL):
    async with ClientSession() as session:
        async with session.get(URL) as preJSData:
            if preJSData.status == 200:
                return await preJSData.json()
            else:
                print(f"BattleMetrics Error [Code {preJSData.status}]")

change_status.start()

client.run(discordBotToken)