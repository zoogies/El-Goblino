#imports
import csv

import discord
import requests
from discord.ext import commands, tasks

#verbose mode
v = False

#static variables
client = discord.Client()
twitchAPIEndpoint = "https://api.twitch.tv/helix/search/channels?query=xqcow"

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

@tasks.loop(hours=24)
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
        #TODO this is where i left off, take the data from this object and load it into a discord message, also add this function to the bindable flow check every like 10 seconds if he went live
        #https://python.plainenglish.io/send-an-embed-with-a-discord-bot-in-python-61d34c711046

    except Exception as e:
        print('El Goblino failed getting the live status, i enjoyed my stay xqcL')
        if v:
            print(e)
        return False

@client.event
async def on_ready():
    print('{0.user} is now online.'.format(client))
    getNewAuthTwitchAPI.start()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$check'):
        livestatus = checkLiveStatus()
        if livestatus:
            await message.channel.send(livestatus)

client.run(discordToken)
