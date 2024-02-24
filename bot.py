from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import os
from dotenv import load_dotenv
load_dotenv()
import realTime

url = 'localhost:3000'


def get_balance(public_key):
    response = requests.get(f'http://{url}/balance/{public_key}')
    return response.json()['balance']


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
    await update.message.reply_text("Usage: /check_balance <public_key>")
TELEGRAM_TOKEN ='7058333666:AAHcrQf9rK6-3fGLwORkbx0Bopwek2q4-Vk'
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("check_balance", check_balance))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("data", realTime.data))
app.add_handler(CommandHandler("chart", realTime.send_chart))
app.run_polling()
