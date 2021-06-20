#imports
import csv
import json

import discord
from discord import message
from discord import channel
import requests
from discord.ext import commands, tasks

class Goblino():
    def __init__(self):
        #verbose mode
        self.verbose = True

        #static variables
        self.client = discord.Client()
        self.username = 'xqcow'
        self.twitchAPIEndpoint = "https://api.twitch.tv/helix/streams?user_login=" + self.username
        self.twitchKeyCooldown = 24 #in hours
        self.checkLiveCooldown = 20 #in seconds
        self.isLive = False
        self.channelName = 'live-notifs'
        
        #declare hidden variables
        self.discordToken = 'loaded from tokens.csv'
        self.twitchSecret = 'loaded from tokens.csv'
        self.twitchAPIheaders = {
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
            self.discordToken = tokens[0]
            self.twitchSecret = tokens[1]
            self.twitchAPIheaders['Client-ID'] = tokens[2]

            #Debug shit, TODO remove
            if self.verbose:
                print(tokens)
                print(self.discordToken)
                print(self.twitchSecret)
                print(self.twitchAPIheaders['Client-ID'])

        except Exception as e:
            print('El Goblino couldnt find the tokens.csv file, make sure it exists')
            if self.verbose:
                print(e)
            exit()

        self.client.run(self.discordToken)
        
    @tasks.loop(hours=self.twitchKeyCooldown)
    async def getNewAuthTwitchAPI(self):
        try:
            newCreds = requests.post('https://id.twitch.tv/oauth2/token?client_id=' + self.twitchAPIheaders['Client-ID'] + '&client_secret=' + self.twitchSecret + '&grant_type=client_credentials')
            newCreds = newCreds.json()
            if self.verbose:
                print(newCreds)
            self.twitchAPIheaders['Authorization'] = 'Bearer '+ newCreds['access_token']
            print('El Goblino just updated the twitch API auth token')
            if self.verbose:
                print(self.twitchAPIheaders)
        except Exception as e:
            print('El Goblino fucked up changing the twitch API auth token, woops')
            if self.verbose:
                print(e)
    
    def checkLiveStatus(self):
        try:
            request = requests.get(self.twitchAPIEndpoint,headers=self.twitchAPIheaders)
            requestReturn = request.json()
            if self.verbose:
                print(requestReturn)

            print('El Goblino just got the live status, i wonder if my juicer is live')

            with open('data.json', 'w') as f:
                json.dump(requestReturn, f)
            
            data = requestReturn['data'][0]
            if self.verbose:
                print(data)

            return data

        except Exception as e:
            print('El Goblino failed getting the live status, i enjoyed my stay xqcL')
            if self.verbose:
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

    @tasks.loop(seconds=self.checkLiveCooldown)
    async def mainLoop(self):
        #get the steam data and update our state
        streamData = checkLiveStatus()
        if streamData:
            #only update our variable for live if he was previously offline
            if streamData['type'] == 'live' and self.isLive == False:
                self.isLive = True
                #send an embed to let me know that hes live
                embed(streamData,channel)
            else:
                self.isLive = False
        else:
            print('Something went wrong when El Goblino tried to recieve the stream data :(')

    @client.event
    async def on_ready():
        print('{0.user} is now online.'.format(self.client))
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

    