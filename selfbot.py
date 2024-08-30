import os
import discord
from discord.ext import tasks, commands
import aiohttp
import asyncio
from io import BytesIO
import requests
import random
import string
import http.client
import json
from pyfiglet import Figlet

bot = commands.Bot(command_prefix=';', self_bot=True, help_command=None)
token = "BOT TOKEN"
litecoin = "LTC ADDY"
paypal = "PAYPAL EMAIL"

EXCHANGE_RATES = {
    'EUR': {'USD': 1.1, 'GBP': 0.85, 'BTC': 0.000027, 'ETH': 0.00037, 'LTC': 0.018},
    'USD': {'EUR': 0.91, 'GBP': 0.77, 'BTC': 0.000024, 'ETH': 0.00034, 'LTC': 0.016},
    'GBP': {'EUR': 1.18, 'USD': 1.30, 'BTC': 0.000031, 'ETH': 0.00044, 'LTC': 0.021},
    'BTC': {'EUR': 37000, 'USD': 37000 * 1.1, 'GBP': 37000 * 0.85, 'LTC': 250},
    'ETH': {'EUR': 2000, 'USD': 2000 * 1.1, 'GBP': 2000 * 0.85, 'LTC': 8},
    'LTC': {'EUR': 55, 'USD': 55 * 1.1, 'GBP': 55 * 0.85, 'BTC': 0.000004, 'ETH': 0.125}
}

CURRENCY_MAP = {
    'euro': 'EUR', 'euros': 'EUR', 'european': 'EUR',
    'usd': 'USD', 'dollar': 'USD', 'dollars': 'USD',
    'gbp': 'GBP', 'pound': 'GBP', 'pounds': 'GBP',
    'bitcoin': 'BTC', 'btc': 'BTC',
    'ethereum': 'ETH', 'eth': 'ETH',
    'litecoin': 'LTC', 'ltc': 'LTC'
}

@bot.event
async def on_ready():
    print(f"{'-'*50}")
    print(f"   Logged in as: {bot.user.name}")
    print(f"   User ID: {bot.user.id}")
    print(f"{'-'*50}")
    print(f"   Username: {bot.user.name}")
    print(f"   Guilds: {len(bot.guilds)}")
    print(f"   Members: {sum([guild.member_count for guild in bot.guilds])}")
    print(f"{'-'*50}")

@bot.command()
async def ltc(ctx, amount: str):
    await ctx.message.delete()
    message = (
        f"> # <a:verification:1277486258246914071> Ltc Instructions\n"
        f"> Instructions for paying {amount}€ via Ltc\n"
        f"> **AMOUNT**: ```{amount}€```\n"
        f"> **SEND TO**: ```{litecoin}```\n"
    )
    await ctx.send(message, delete_after=120)

@bot.command()
async def pp(ctx, amount: str):
    await ctx.message.delete()
    message = (
        f"> # <a:verification:1277486258246914071> PayPal Instructions\n"
        f"> Instructions for paying {amount}€ via PayPal\n"
        f"> **AMOUNT**: ```{amount}€```\n"
        f"> **SEND TO**: ```{paypal}```\n"
        f"> **NOTES**: \n> Must send using Friends & Family, Must send using paypal balance, No notes\n"
    )
    await ctx.send(message, delete_after=120)

@bot.command(name='spam')
async def spam(ctx, amount: int, *, message: str):
    await ctx.message.delete()
    if amount <= 0:
        await ctx.send("Please provide a positive number for the amount.", delete_after=15)
        return
    if amount > 100:
        await ctx.send("Please don't spam too much. Limit is 100 messages.", delete_after=15)
        return
    for _ in range(amount):
        await ctx.send(message, delete_after=15)
        await asyncio.sleep(0.5)

@bot.command(name='userinfo')
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_info = [
        f"> # <a:verification:1277486258246914071> USER INFO FOR {member}",
        f"> - Username: {member.name}",
        f"> - Discriminator: {member.discriminator}",
        f"> - ID: {member.id}",
        f"> - Nickname: {member.nick or 'None'}",
        f"> - Status: {member.status}",
        f"> - Joined Discord: <t:{int(member.created_at.timestamp())}:d>",
        f"> - Joined Server: <t:{int(member.joined_at.timestamp())}:d>"
    ]
    response = '\n'.join(user_info)
    await ctx.send(f"{response}", delete_after=15)
    await ctx.message.delete()  # Deletes the command message
    
@bot.command(name='serverinfo')
async def serverinfo(ctx):
    guild = ctx.guild
    if guild:
        server_info = [
            f"> # <a:verification:1277486258246914071> SERVER INFO FOR {guild.name}",
            f"> - Server ID: {guild.id}",
            f"> - Owner: {guild.owner} ({guild.owner_id})",
            f"> - Member Count: {guild.member_count}",
            f"> - Boost Count: {guild.premium_subscription_count}",
            f"> - Created On: <t:{int(guild.created_at.timestamp())}:d>",
            f"> - Region: {guild.region}"
        ]
        response = '\n'.join(server_info)
        await ctx.send(f"{response}", delete_after=15)
    else:
        await ctx.send("Unable to fetch server info.", delete_after=15)
    await ctx.message.delete()  # Deletes the command message

@bot.command()
async def purge(ctx, limit: int = 100):
    await ctx.message.delete()
    if ctx.author.bot:
        return
    deleted = 0
    async for msg in ctx.channel.history(limit=limit):
        if msg.author == ctx.author:
            try:
                await msg.delete()
                deleted += 1
            except discord.Forbidden:
                await ctx.send("I do not have permission to delete messages.", delete_after=15)
            except discord.HTTPException as e:
                await ctx.send(f"Failed to delete a message: {e}", delete_after=15)
    await ctx.send(f"> # <a:verification:1277486258246914071> PURGE\n> Purged {deleted} messages.", delete_after=15)

@bot.command(name='help')
async def info(ctx):
    await ctx.message.delete()
    help_message = (
        f"# <a:verification:1277486258246914071> COMMAND LIST\n"
        f"> **- litecoin** - Sends a request to send the specified amount of € to a Litecoin address.\n"
        f"> **- paypal** - Sends a request to send the specified amount of € to a PayPal address.\n"
        f"> **- convert [currency] [amount]** - Converts the specified amount of Euro or USD to GBP.\n"
        f"> **- fee** - Adds a custom fee % to number.\n"
        f"> **- ltcprice** - Gets the current price of Litecoin.\n"
        f"> **- bal** - Checks the balance of a crypto address.\n"
        f"> **- math** - Does math.\n"
        f"> **- coinflip** - Flips a coin.\n"
        f"> **- number** - Generates a random number from 1 to 100.\n"
        f"> **- asci** - Generates asci text.\n"
        f"> **- serverinfo [server_id]** - Provides information about the specified server.\n"
        f"> **- userinfo [user]** - Provides information about the specified user.\n"
        f"> **- purge [limit]** - Deletes a specified number of messages from the channel (defaults to 100).\n"
        f"> **- scrap <amount>** - Creates a transcript of the amount of messages.\n"
        f"> **- spam [amount] [message]** - Sends the specified message multiple times (up to 100).\n"
        f"> **- info** - Displays this help message.\n"
    )
    await ctx.send(help_message, delete_after=30)

@bot.command(name='vouch')
async def review(ctx, *args):
    if len(args) < 3:
        await ctx.send("Usage: +review <product> <type> <price>", delete_after=15)
        return
    product = ' '.join(args[:-2])
    type = args[-2]
    price = args[-1]
    await ctx.message.delete()
    message = (
        f"> # <a:verification:1277486258246914071> Thank You for Your Purchase!\n"
        f"> Thank you for purchasing **{product} {type}** for **{price}€**. We hope you enjoy your purchase! "
        f"Please leave a review to let others know your experience while using **Boostinz!**\n"
        f"> Use the following vouch command in <#1274029370192691290>:\n"
        f"> ```+vouch @{ctx.author.name} {product} {type} | {price}€```"
    )
    await ctx.send(message, delete_after=120)
    
@bot.command(name='fee')
async def calculate_fee(ctx, operation: str, fee: float, amount: float):
    if operation == '+':
        fee_amount = (fee / 100) * amount
        total_amount = amount + fee_amount
        operation_text = "added to"
    elif operation == '-':
        fee_amount = (fee / 100) * amount
        total_amount = amount - fee_amount
        operation_text = "removed from"
    else:
        await ctx.send("Invalid operation! Use `+` to add a fee or `-` to remove a fee.", delete_after=10)
        return
    response = (
        f"> # <a:verification:1277486258246914071> FEE CALCULATION\n"
        f"> **{fee:.2f}%** fee {operation_text} **{amount:.2f}€** = **{total_amount:.2f}€**.\n"
    )
    await ctx.send(response, delete_after=15)
    await ctx.message.delete()

@bot.command(name='math')
async def perform_math(ctx, num1: float, operation: str, num2: float):
    try:
        if operation == '+':
            result = num1 + num2
        elif operation == 'x':
            result = num1 * num2
        else:
            await ctx.send("Invalid operation. Use `+` for addition or `x` for multiplication.", delete_after=15)
            return
        response = (
            f"> # <a:verification:1277486258246914071> MATH CALCULATION\n"
            f"> **{num1:.2f}** {operation} **{num2:.2f}** = **{result:.2f}**.\n"
        )
        await ctx.send(response, delete_after=15)
    except Exception as e:
        await ctx.send(f"An error occurred: {e}", delete_after=15)
    await ctx.message.delete()

@bot.command()
async def ltcprice(ctx):
    url = 'https://api.coingecko.com/api/v3/coins/litecoin'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        price = data['market_data']['current_price']['eur']
        await ctx.send(f"> # <a:verification:1277486258246914071> LTC PRICE\n> The current price of Litecoin is {price:.2f}€", delete_after=15)
        await ctx.message.delete()

@bot.command()
async def ltcbal(ctx, ltcaddress):
    response = requests.get(f'https://api.blockcypher.com/v1/ltc/main/addrs/{ltcaddress}/balance')
    if response.status_code == 200:
        data = response.json()
        balance = data['balance'] / 10**8
        total_balance = data['total_received'] / 10**8
        unconfirmed_balance = data['unconfirmed_balance'] / 10**8
    else:
        return
    coingecko_response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=eur')
    if coingecko_response.status_code == 200:
        eur_price = coingecko_response.json()['litecoin']['eur']
    else:
        return
    eur_balance = balance * eur_price
    eur_total_balance = total_balance * eur_price
    eur_unconfirmed_balance = unconfirmed_balance * eur_price
    message = f"> # <a:verification:1277486258246914071> LTC BALANCE\n"
    message += f"> - LTC Address: `{ltcaddress}`\n"
    message += f"> - Current Balance: **{balance:.8f} LTC** (**€{eur_balance:.2f} EUR**)\n"
    message += f"> - Total Received: **{total_balance:.8f} LTC** (**€{eur_total_balance:.2f} EUR**)\n"
    message += f"> - Unconfirmed Balance: **{unconfirmed_balance:.8f} LTC** (**€{eur_unconfirmed_balance:.2f} EUR**)"
    await ctx.send(message, delete_after=15)
    await ctx.message.delete()
    
@bot.command()
async def scrap(ctx, number: int):
    channel = ctx.channel
    if number <= 0 or number > 10000:
        await ctx.send("Please provide a valid number between 1 and 10,000.")
        await ctx.message.delete()
        return
    try:
        messages = []
        async for message in channel.history(limit=number):
            messages.append(f"{message.author}: {message.content}")
        content = "\n".join(messages)
        with open("scraped_messages.txt", "w", encoding="utf-8") as file:
            file.write(content)
        await asyncio.sleep(1)  
        with open("scraped_messages.txt", "rb") as file:
            await ctx.send(file=discord.File(file, filename="scraped_messages.txt"))
        await ctx.message.delete()  # Delete the command message after sending the file
    except discord.Forbidden:
        await ctx.send("I don't have permission to access the channel.")
        await ctx.message.delete()
    except discord.HTTPException:
        await ctx.send("An error occurred while fetching messages.")
        await ctx.message.delete()
    except Exception as e:
        await ctx.send(f"An error occurred: {str(e)}")
        await ctx.message.delete()

@bot.command(name='coinflip')
async def coinflip(ctx):
    await ctx.send(random.choice(['Heads', 'Tails']))
    await ctx.message.delete()
def generate_random_string(length=16):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@bot.command(name='number')
async def number(ctx):
    await ctx.send(random.randint(1, 100))
    await ctx.message.delete()
    
@bot.command(name='exchange')
async def convert(ctx, amount: float, from_currency: str, to_currency: str):
    from_currency = from_currency.lower()
    to_currency = to_currency.lower()
    from_currency = CURRENCY_MAP.get(from_currency, from_currency.upper())
    to_currency = CURRENCY_MAP.get(to_currency, to_currency.upper())
    if from_currency not in EXCHANGE_RATES or to_currency not in EXCHANGE_RATES[from_currency]:
        await ctx.send(f'Invalid currency pair: {from_currency} to {to_currency}')
        return
    conversion_rate = EXCHANGE_RATES[from_currency].get(to_currency)
    if not conversion_rate:
        await ctx.send(f'Conversion rate not available for {from_currency} to {to_currency}')
        return
    converted_amount = amount * conversion_rate
    rounded_amount = round(converted_amount, 8)
    response = (f"> # <a:verification:1277486258246914071> CONVERT\n"
                f"> **{amount:.2f} {from_currency}** is = to **{rounded_amount:.8f} {to_currency}**")
    await ctx.send(response, delete_after=15)
    await ctx.message.delete()

@bot.command()
async def asci(ctx, *, text):
    f = Figlet(font='standard')
    ascii_art = f.renderText(text)
    await ctx.send(f'```{ascii_art}```')
    await ctx.message.delete()
    
CHANNEL_ID = 1278478798479818803 
MESSAGE_TEXT = "# <a:verification:1277486258246914071> SENDING THIS MESSAGE EVERY 3 SECONDS"
    
@tasks.loop(seconds=3)  # Change the interval to 3 seconds
async def send_message():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is not None:
        await channel.send(MESSAGE_TEXT)
    else:
        print(f"Channel with ID {CHANNEL_ID} not found.")

@bot.command(name='messagestart')
async def message_start(ctx):
    if not send_message.is_running():
        send_message.start()
        await ctx.send("Started sending messages every 3 seconds.")
    else:
        await ctx.send("Messages are already being sent.")
        await ctx.message.delete()

@bot.command(name='messagestop')
async def message_stop(ctx):
    if send_message.is_running():
        send_message.stop()
        await ctx.send("Stopped sending messages.")
    else:
        await ctx.send("Messages are not currently being sent.")
        await ctx.message.delete()


bot.run(token)