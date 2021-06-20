#imports
import csv
import json

import discord
from discord import message
from discord import channel
import requests
from discord.ext import commands, tasks

#verbose mode
v = True

#static variables
client = discord.Client()
username = 'xqcow'
twitchAPIEndpoint = "https://api.twitch.tv/helix/streams?user_login=" + username
twitchKeyCooldown = 24 #in hours
checkLiveCooldown = 20 #in seconds
isLive = False
channelName = 'live-notifs'

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

    #Debug shit, TODO remove
    if v:
        print(tokens)
        print(discordToken)
        print(twitchSecret)
        print(twitchAPIheaders['Client-ID'])

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

        print(requestReturn)
        with open('data.json', 'w') as f:
            json.dump(requestReturn, f)
        
        data = requestReturn['data'][0]
        if v:
            print(data)
        return data

        #TODO this is where i left off, take the data from this object and load it into a discord message, also add this function to the bindable flow check every like 10 seconds if he went live
        #https://python.plainenglish.io/send-an-embed-with-a-discord-bot-in-python-61d34c711046

    except Exception as e:
        print('El Goblino failed getting the live status, i enjoyed my stay xqcL')
        if v:
            print(e)
        return False

def embed(streamData,channel):

    title = streamData['title']
    url = 'https://www.twitch.tv/xqcow'
    description = 'xQcOW has gone live!'

    embed=discord.Embed(title=title, url=url, description=description, color=0x20fc03)
    if channel:
        channel.send(embed)
    else:
        print('El goblino couldnt send a message to the channel because it hasnt been set')

@tasks.loop(seconds=checkLiveCooldown)
async def mainLoop(isLive,channel):
    #get the steam data and update our state
    streamData = checkLiveStatus()
    if streamData:
        #only update our variable for live if he was previously offline
        if streamData['type'] == 'live' and isLive == False:
            isLive = True
            #send an embed to let me know that hes live
            embed(streamData,channel)
        else:
            isLive = False
    else:
        print('Something went wrong when El Goblino tried to recieve the stream data :(')

@client.event
async def on_ready():
    print('{0.user} is now online.'.format(client))
    getNewAuthTwitchAPI.start()
    mainLoop.start(isLive,channel)

def setChannel(channel):
    channel = channel

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('GOBLIN INITIATE'):
        setChannel(message.chanel)
        await message.channel.send('Goblin is now craling around in "'+str(message.channel)+'"')

client.run(discordToken)