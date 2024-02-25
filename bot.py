import realTime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import os
from dotenv import load_dotenv
import solRag
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_KEY")

map_coin = {
    "btc": "bitcoin",
    "eth": "ethereum",
    "sol": "solana",
    "ada": "cardano",
    "bnb": "binancecoin",
    "usdt": "tether",
    "xrp": "ripple",
    "doge": "dogecoin",
    "dot": "polkadot",
    "usdc": "usd-coin",
    "uni": "uniswap",
    "bch": "bitcoin-cash",
    "ltc": "litecoin",
    "link": "chainlink",
    "matic": "polygon",
    "xlm": "stellar",
    "vet": "vechain",
    "cro": "crypto-com-chain",
    "trx": "tron",
    "fil": "filecoin",
    "ftt": "ftx-token",
    "theta": "theta-token"
}


url = 'localhost:3000'
server_url = 'http://112.137.129.161:6789/imagine?prompt='

def get_balance(public_key):
    response = requests.get(f'http://{url}/balance/{public_key}')
    return response.json()['balance']

async def gen_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if len(args) == 0:
        await update.message.reply_text("Please provide a prompt to generate an image")
        return
    prompt = " ".join(args)
    response = requests.get(server_url + prompt)
    await update.message.reply_photo(response.content)  




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to the Solana Cookbook Bot! You can use /help to see the available commands."
    )


async def askSolana(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    args = context.args
    if len(args) == 0:
        await update.message.reply_text("Please provide a question")
        return

    question = " ".join(args)
    response = solRag.get_response(question)
    await update.message.reply_text(response)



async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name} vap')


async def check_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Extract the public key from the command message
    args = context.args
    if len(args) != 1:
        await update.message.reply_text("Usage: /check_balance <public_key>")
        return
    public_key = args[0]

    try:
        balance = get_balance(public_key)
        await update.message.reply_text(f'Balance of the account at {public_key} is {balance} SOL')
    except Exception as e:
        await update.message.reply_text(f'Failed to retrieve balance: {str(e)}')


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = """Usage:
                /check_balance <public_key> - Check balance
                /hello - Say hello
                /askSolana - Ask something about Solana
                /data - Get real-time value coin 
                /chart - Send a chart
                """
    await update.message.reply_text(message)



app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("check_balance", check_balance))
app.add_handler(CommandHandler("askSolana", askSolana))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("gen_image", gen_image))
app.add_handler(CommandHandler("data", realTime.data))
app.add_handler(CommandHandler("chart", realTime.send_chart))
app.run_polling()
