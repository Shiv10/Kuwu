#import json
import discord
from discord.ext import commands, tasks
import os, asyncio
from dotenv import load_dotenv
import threading, time
from flask import Flask, request
load_dotenv()

app = Flask(__name__)

global monitor_data
monitor_data = {}

global tags
tags = []


@app.route('/', methods=['POST', 'GET'])
def get_data():
    if request.method == 'POST':
        c={}
        c['client_addr']=request.environ['REMOTE_ADDR']
#       req_data = request.get_json()
        data = str(request.form['stats']).split(',')
        l = len(data)
        i = 4
        while (i<l):
            c[data[i].strip()]=data[i+1:i+4]
            i+=4
        global monitor_data
        monitor_data = c
        global tags
        t = str(request.form['ids']).split(',')
        for j in t:
            tags.append(j.strip())
        print('data has been recieved!')
        return "data recieved!"
    return "Hello Test!"

def run_server():
    if __name__ == '__main__':
        app.run(host=os.getenv('HOST'),port=os.getenv('PORT'))

t1  = threading.Thread(target=run_server)
t1.start()

client = commands.Bot(command_prefix='.')

@client.event
async def on_ready():
    monitorChallenges.start()
    challengeStatus.start()
    await client.change_presence(status =  discord.Status.online, activity=discord.Game('Type .list to list all commands'))
    print('Bot is ready')


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@tasks.loop(seconds = 60)
async def challengeStatus():

    print('testing')
    statusChannel = client.get_channel(int(os.getenv('CHALLENGE_STATUS_CHANNEL')))
    w = ''
    table = [['TAGS','CONTAINER ID','Name', 'CPU %', 'MEM%']]

    if monitor_data == {}:
        return

    
    for i in dict.keys(monitor_data):
        
        if (i == 'client_addr'):
            continue
        
        print(tags[tags.index(i)-1])
        table.append([tags[tags.index(i)-1], i, monitor_data[i][0], monitor_data[i][1], monitor_data[i][2]])
    
    for row in table:
        w += "{: >20} {: >20} {: >20} {: >20} {: >20}".format(*row)+'\n'

    print('hello world!')

    clientIp = monitor_data['client_addr']
    w += f'\n\nData recieved from I.P {clientIp}'

    await statusChannel.send(w) #send challenge data here!
    print(w)


@tasks.loop(seconds = 15)
async def monitorChallenges():
    
    if(monitor_data == {}):
        return
    

    channel = client.get_channel(int(os.getenv('CHALLENGE_STATUS_CHANNEL')))

    print('not returned')

    for i in dict.keys(monitor_data):
        if (i == 'client_addr' or  i == 'CONTAINER'):
            continue

        if(float(monitor_data[i][1][0:-1]) > 50.00):
            await channel.send(f'{monitor_data[i][0]} has a CPU usage of {monitor_data[i][1]}.\n Please check. \nID: {i}')

        if (float(monitor_data[i][2][0:-1]) > 60.00):
            await channel.send(f'{monitor_data[i][0]} has a memory usage of {monitor_data[i][4]}\nPlease check.\nID: {i}')

            

@tasks.loop(seconds = 10)
async def print_something():
    print("hello")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('All required arguments not passed.')
        return
    
    if isinstance(error, commands.BadArgument):
        await ctx.send('Arguments sent not correct.')
        return
    
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Command does not exist.')
        return

    if isinstance(error, commands.CommandInvokeError):
        await ctx.send('Bot does not have permissions to kick/ban people. Please grant permissions')
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('Bot does not have permissions to perform the task. Please give permission')

async def firstBlood(userName, challengeName):
    channel = client.get_channel(int(os.getenv('FIRST_BLOOD_CHANNEL')))
    await channel.send(f'{userName} got first blood in challenge: {challengeName}')
    


client.run(os.getenv('TOKEN'))

#https://discord.com/oauth2/authorize?client_id=723828224307757178&scope=bot
