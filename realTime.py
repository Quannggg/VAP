import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import requests
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt

import pandas as pd
import io 
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

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
async def send_chart(update: Update, context: CallbackContext) -> None:
    if context.args:
        coin_name = context.args[0].lower()
        coin_name = map_coin.get(coin_name, coin_name)
        coin_info = get_coin_info(coin_name)
        if coin_info:
            changes = {
                'Period': ['24h', '7d', '14d', '30d', '60d', '1y'],
                'Price Change (%)': [
                    coin_info['market_data']['price_change_percentage_24h'],
                    coin_info['market_data']['price_change_percentage_7d'],
                    coin_info['market_data']['price_change_percentage_14d'],
                    coin_info['market_data']['price_change_percentage_30d'],
                    coin_info['market_data']['price_change_percentage_60d'],
                    coin_info['market_data']['price_change_percentage_1y']
                ]
            }

            df = pd.DataFrame(changes)

            plt.figure(figsize=(5, 3))
            plt.plot(df['Period'], df['Price Change (%)'], marker='o', linestyle='-', color='b')
            plt.title(f'{coin_name.capitalize()} Price Change % Over Different Periods')
            plt.xlabel('Period')
            plt.ylabel('Price Change (%)')
            plt.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=300)
            buf.seek(0)

            await update.message.reply_photo(photo=buf)

            buf.close()
            plt.clf()
        else:
            await update.message.reply_text(f"Sorry, I couldn't fetch the data for {coin_name}.")
    else:
        await update.message.reply_text("Please specify a coin name. Usage: /chart <coinname>")

def get_coin_info(coin_name):
    """Fetch detailed information about a cryptocurrency from the CoinGecko API."""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        logger.error(f"Error fetching data for {coin_name}: {e}")
        return None

async def data(update: Update, context: CallbackContext) -> None:
    if context.args:
        coin_name = context.args[0].lower()
        coin_name = map_coin.get(coin_name, coin_name)
        coin_info = get_coin_info(coin_name)
        if coin_info:
            # Crafting a detailed message. Adjust according to your needs to avoid exceeding message length limits.
            message = f"Name: {coin_info['name']} ({coin_info['symbol'].upper()})\n"
            message += f"Current Price: ${coin_info['market_data']['current_price']['usd']} USD\n"
            message += f"Market Cap: ${coin_info['market_data']['market_cap']['usd']} USD\n"
            message += f"Trading Volume (24h): ${coin_info['market_data']['total_volume']['usd']} USD\n"
            message += f"Circulating Supply: {coin_info['market_data']['circulating_supply']}\n"
            message += f"Total Supply: {coin_info['market_data'].get('total_supply', 'N/A')}\n"
            message += f"Max Supply: {coin_info['market_data'].get('max_supply', 'N/A')}\n"
            message += f"Change (24h): {coin_info['market_data']['price_change_percentage_24h']}%\n"
            message += f"Change (7d): {coin_info['market_data']['price_change_percentage_7d']}%\n"
            message += f"Change (14d): {coin_info['market_data']['price_change_percentage_14d']}%\n"
            message += f"Change (30d): {coin_info['market_data']['price_change_percentage_30d']}%\n"
            message += f"Change (60d): {coin_info['market_data']['price_change_percentage_60d']}%\n"
            message += f"Change (1y): {coin_info['market_data']['price_change_percentage_1y']}%\n"
            message += f"Homepage: {coin_info['links']['homepage'][0]}\n"
            message += f"Blockchain Site: {coin_info['links']['blockchain_site'][0]}\n"
            message += f"Official Forum: {coin_info['links']['official_forum_url'][0]}"
            await update.message.reply_text(message)
        else:
            await update.message.reply_text("Sorry, I couldn't fetch the data for that coin.")
    else:
        await update.message.reply_text("Please specify a coin name. Usage: /data <coinname>")
