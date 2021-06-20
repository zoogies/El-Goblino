#imports
import csv
import json

import discord
from discord import message
from discord import channel
import requests
from discord.ext import commands, tasks

#verbose mode
v = False

#static variables
client = discord.Client()
#username = 'xqcow'
username = 'xqcow'
twitchAPIEndpoint = "https://api.twitch.tv/helix/streams?user_login=" + username
twitchKeyCooldown = 24 #in hours
checkStatusCooldown = 20
cooldownWhenOffline = 20 #in seconds
cooldownWhenLive = 60
isLive = False

#declare hidden variables
discordToken = 'loaded from tokens.csv'
twitchSecret = 'loaded from tokens.csv'
twitchAPIheaders = {
    'Client-ID' : 'loaded from tokens.csv',
    'Authorization' : 'tgenerated upon running',
}


#dynamic variables loaded in via tokens.csv
try:
    #create our reader and read our values from the csv file inside /src
    tokenFile = open("src/tokens.csv", "r")
    csv_reader = csv.reader(tokenFile)
    tokensList = []
    for row in csv_reader:
        tokensList.append(row)
    tokens = tokensList[0]

    #use our tokens to assign variables values
    discordToken = tokens[0]
    twitchSecret = tokens[1]
    twitchAPIheaders['Client-ID'] = tokens[2]
    channel = (int(tokens[3]))
    #Debug shit, TODO remove
    if v:
        print(tokens)
        print(discordToken)
        print(twitchSecret)
        print(twitchAPIheaders['Client-ID'])
        print(int(tokens[3]))
        print(channel)

except Exception as e:
    print('El Goblino couldnt find the tokens.csv file, make sure it exists')
    if v:
        print(e)
    exit()

@tasks.loop(hours=twitchKeyCooldown)
async def getNewAuthTwitchAPI():
    try:
        newCreds = requests.post('https://id.twitch.tv/oauth2/token?client_id=' + twitchAPIheaders['Client-ID'] + '&client_secret=' + twitchSecret + '&grant_type=client_credentials')
        newCreds = newCreds.json()
        if v:
            print(newCreds)
        twitchAPIheaders['Authorization'] = 'Bearer '+ newCreds['access_token']
        print('El Goblino just updated the twitch API auth token')
        if v:
            print(twitchAPIheaders)
    except Exception as e:
        print('El Goblino fucked up changing the twitch API auth token, woops')
        if v:
            print(e)
    

def checkLiveStatus():
    try:
        request = requests.get(twitchAPIEndpoint,headers=twitchAPIheaders)
        requestReturn = request.json()
        if v:
            print(requestReturn)
        print('El Goblino just got the live status, i wonder if my juicer is live')

        with open('data.json', 'w') as f:
            json.dump(requestReturn, f)
        try:
            data = requestReturn['data'][0]
        except:
            return #TODO stream data returns whats in the json rn when not live.
        if v:
            print(data)
        return data

    except Exception as e:
        print('El Goblino failed getting the live status, i enjoyed my stay xqcL')
        if v:
            print(e)
        return False

async def embed(streamData,channel):
    channel = client.get_channel(channel)

    title = streamData['title']
    url = 'https://www.twitch.tv/xqcow'
    description = 'xQcOW is now live!'
    image = "https://pbs.twimg.com/profile_images/1188911868863221772/fpcyKuIW_400x400.jpg"
    game = streamData["game_name"]

    embed=discord.Embed(title=title, url=url, description=description, color=0x20fc03)
    embed.set_thumbnail(url=image)
    embed.set_author(name="xQcOW has gone live!", url="https://www.twitch.tv/xqcow", icon_url="https://pbs.twimg.com/profile_images/1188911868863221772/fpcyKuIW_400x400.jpg")
    embed.set_thumbnail(url="https://i.popdog.com/0777a661-6332-11ea-ae2b-0a58a9feac2a")
    embed.add_field(name="Playing", value=game, inline=True)
    embed.set_footer(text="Get the juice baby 😈")
    await channel.send(embed=embed)

@tasks.loop(seconds=checkStatusCooldown)
async def mainLoop(channel):
    #get the steam data and update our state
    streamData = checkLiveStatus()
    global isLive

    if streamData != None:
        #only update our variable for live if he was previously offline
        if streamData['type'] == 'live' and isLive == False:
            isLive = True
            checkLiveCooldown = cooldownWhenLive
            #send an embed to let me know that hes live
            await embed(streamData,channel)
    else:
        print('Juicer is offline :(')
        isLive = False
        checkLiveCooldown = cooldownWhenOffline

@client.event
async def on_ready():
    print('{0.user} is now online.'.format(client))
    getNewAuthTwitchAPI.start()
    mainLoop.start(channel)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('GOBLIN INITIATE'):
        await message.channel.send('Goblin is now craling around in "'+str(message.channel)+'"')

client.run(discordToken)