from trade_platforms.ftx_wrapper import FTX
from bots.hello_bot import HelloBot
from bots.bot_base import Mode

if __name__ == "__main__":
    bot = HelloBot(platforms=[
        FTX(name="FTX BTCUSD", base_currency="BTC", quote_currency="USD")
    ],
    mode=Mode.Test)
    bot.run()
    print("Exiting application...")