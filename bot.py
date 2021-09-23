import json
import discord
import requests
import threading
import json
from discord.ext import commands,tasks
from dotenv import load_dotenv
from random import randint
import os
import time

load_dotenv()

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.presences = True
intents.dm_messages = True
intents.messages = True
intents.all()

client = commands.Bot(command_prefix='.', intents=intents)

opensea_url_assets = "https://api.opensea.io/api/v1/assets"
opensea_url_collections = "https://api.opensea.io/api/v1/collections"
contract_address = '0xE020adb9e242702F1284440CF80dF635E9a458c3'
creator_address = '0x58B6fC6b777A35ea50F0BFB218e5Ef8CEc1A7578'

collection_items = {}
data_is_ready = False

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


def get_totaly_supply():
    querystring = {"asset_owner":"0x58B6fC6b777A35ea50F0BFB218e5Ef8CEc1A7578","offset":"0","limit":"300"}
    response = requests.request("GET", opensea_url_collections, params=querystring)
    data = json.loads(response.text)
    total_supply = 3333
    for item in data:
        if item['slug'] == 'cryptobearsofficial':
            total_supply = item['stats']['count']
            return total_supply

    return total_supply





def load_opensea_data():
   
    global collection_items, data_is_ready
    while True:
        print('Loading OpenSea Data')
        offset = 0
        limit = 50
        querystring = {"order_direction":"asc","offset":f"{offset}","limit":f"{limit}","asset_contract_address":f"{contract_address}"}

        temp_coll = {}

        
        total_supply = get_totaly_supply()
        try:
            while offset < total_supply:
                response = requests.request("GET",opensea_url_assets,params=querystring)
                data = json.loads(response.text)
                for asset in data["assets"]:
                    token_id = asset['token_id']
                    traits = asset['traits']
                    rarity = 0
                    for trait in traits:
                        rarity += (trait['trait_count'] / total_supply) * 100
                    rarity /= len(traits)
                    temp_coll[token_id] = rarity
                offset+=50
                querystring = {"order_direction":"asc","offset":f"{offset}","limit":f"{limit}","asset_contract_address":f"{contract_address}"}
            
            collection_items = dict(sorted(temp_coll.items(),key=lambda x:x[1]))
            data_is_ready = True
            print('Data Finished Loading')
            time.sleep(3600)
        except Exception as e:
            time.sleep(60)
            pass
        
@client.command(aliases=['link'], pass_context=True)
async def get_link(ctx,token: int):
    try:
        if token < 0 or token > 3333:
            ctx.send("Not Possible To Generate That Link!")
        else:
            await ctx.send(f"https://opensea.io/assets/0xe020adb9e242702f1284440cf80df635e9a458c3/{token}")
    except Exception as e:
        print(e)
        await ctx.send("Something went wrong! Oops!")

@client.command(aliases=['minted'], pass_context=True)
async def get_supply(ctx):
    if data_is_ready:
        try:
            await ctx.send(f"Total Bears Minted: {get_totaly_supply()}")
        except Exception as e:
            print(e)
            await ctx.send("Something went wrong! Oops!")


@client.command(aliases=['rarity'], pass_context=True)
async def get_rarity(ctx, token: int):
    if data_is_ready:
        try:
            ranking = list(collection_items.keys()).index(str(token))
            rarity = collection_items[str(token)]
            await ctx.send(f"CryptoBear #{token} is currently ranked {ranking} with an average rating of {rarity}.")
        except Exception as e:
            await ctx.send("Something went wrong(That bear might not be added yet)! Oops. Contact PapaBear!")
    else:
        await ctx.send("Rarity is currenty loading!, Please Wait!")

@client.command(aliases=['raritylb'],pass_context = True)
async def get_leaderboard(ctx):
    if data_is_ready:
        try:
            message = ""
            ranking = list(collection_items.keys())
            i = 1
            for rank in ranking:
                if i == 10:
                    message += f"Rank #{i}:CryptoBear #{rank}, Avg Rarity: {collection_items[rank]}"
                else:
                     message += f"Rank #{i}:CryptoBear #{rank}, Avg Rarity: {collection_items[rank]}\n"
                i+=1
                if i > 10:
                    break

            lb= f"```{message}```"
            await ctx.send(lb)
        except Exception as e:
            print(e)
            await ctx.send("Something went wrong(That bear might not be added yet)! Oops. Contact PapaBear!")
    else:
        await ctx.send("Rarity is current loading!, PLease Wait!")

@client.event
async def on_message(message):
    await client.process_commands(message)           




    
            

    



# @client.event
# async def on_message(message):
#     if message.author == client.user:
#         return

#     author = message.author
#     if "ALMIGHTY BEARS" in [y.name for y in author.roles]:
#         pass

    
#     await message.author.send("Testing!")
    
x = threading.Thread(target=load_opensea_data,daemon=True)
x.start() 
client.run(os.getenv('TOKEN'))

