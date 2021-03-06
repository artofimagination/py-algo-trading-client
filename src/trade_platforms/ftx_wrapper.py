from dotenv import load_dotenv
import os
import pandas as pd
import requests
from typing import List
from trade_platforms.ftx_client import FtxClient
from trade_platforms.platform_wrapper_base import PlatformWrapper


## FTX wrapper on the original ftx client from here
#  https://github.com/ftexchange/ftx/blob/master/rest/client.py
class FTX(PlatformWrapper):
    def __init__(self, base_currency, quote_currency):
        super(FTX, self).__init__(f'FTX-{base_currency}-{quote_currency}')
        self.api_url = 'https://ftx.com/api/markets'
        # Load env to get API key
        load_dotenv()
        self.api_key = os.getenv("FTX_API_KEY")
        self.api_secret = os.getenv("FTX_API_SECRET")
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        if self.base_currency is None or self.quote_currency is None:
            raise Exception(f"Market not selected. \"base_currency\" is {self.base_currency}\
and \"quote_currency\" is {self.quote_currency}")

    ## Returns the market data.
    def market_data(self):
        # Specify the base and quote currencies to get single market data
        request_url = f'{self.api_url}/{self.base_currency}/{self.quote_currency}'
        return pd.DataFrame(requests.get(request_url).json())

    ## Get historical data
    #  @param start_date starting date of the data
    #  @param end_date end date of the data
    #  @param resolution of the data
    def historical_data(self, start_time, end_time, resolution):
        # Specify the base and quote currencies to get single market data
        request_url = f'{self.api_url}/{self.base_currency}/{self.quote_currency}'

        if end_time is None:
            request = \
                f'{request_url}/candles?resolution={resolution}&start_time={start_time}'
        else:
            request = \
                f'{request_url}/candles?resolution={resolution}\
&start_time={start_time}&end_time={end_time}'
        # Get the historical market data as JSON
        historical = requests.get(request).json()
        if historical['success'] is False:
            raise Exception(historical['error'])

        # Convert JSON to Pandas DataFrame
        return pd.DataFrame(historical['result'])

    ## Returns the order history.
    #  @param side filter by side ("buy"/"sell")
    #  @param order_type filter by type order ("limit")
    #  @param start_time starting date of the history
    #  @param end_time end date of the history.
    def get_order_history(
            self,
            side: str = None,
            order_type: str = None,
            start_time: float = None,
            end_time: float = None) -> List[dict]:
        ftx_client = FtxClient(
            api_key=self.api_key,
            api_secret=self.api_secret)
        return pd.DataFrame(ftx_client.get_order_history(
            f"{self.base_currency}/{self.quote_currency}",
            side,
            order_type,
            start_time,
            end_time))

    ## Places the order
    #   @param side   the value can be "sell" or "buy"
    #   @param price  price of the order
    #   @param volume volume of the order
    def place_order(self, type, side, price, volume):
        ftx_client = FtxClient(
            api_key=self.api_key,
            api_secret=self.api_secret)
        # Place an order
        try:
            order_result = ftx_client.place_order(
                market=f"{self.base_currency}/{self.quote_currency}",
                side=side,
                price=price,
                size=volume,
                type=type
            )
        except Exception as e:
            print(f'Error making order request: {e}')
            return None
        return order_result

    ## Cancels the order
    def cancel_order(self, order):
        ftx_client = FtxClient(
            api_key=self.api_key,
            api_secret=self.api_secret)
        try:
            co_result = ftx_client.cancel_order(
                order_id=order['id']
            )
            print(co_result)
        except Exception as e:
            print(f'Error cancelling order request: {e}')

    ## Gets the current price from the platform wrapper.
    def fetch_current_price(self):
        request_url = f'{self.api_url}/{self.base_currency}/{self.quote_currency}'
        market = requests.get(request_url).json()
        current_price = market['result']['price']
        return current_price

    ## Returns all wallet balances.
    def get_balances(self):
        ftx_client = FtxClient(
            api_key=self.api_key,
            api_secret=self.api_secret)
        data = ftx_client.get_wallet_balances()
        wallets = dict()
        for wallet in data:
            wallets[wallet['coin']] = wallet
        return wallets

    ## Returns the account info.
    def get_account_info(self):
        ftx_client = FtxClient(
            api_key=self.api_key,
            api_secret=self.api_secret)
        return ftx_client.get_account_info()

    ## Returns the orderbook of bids and asks.
    def fetch_orderbook(self, depth):
        request_url = f'{self.api_url}/{self.base_currency}/\
{self.quote_currency}/orderbook?depth={depth}'
        data = requests.get(request_url).json()
        orderbook = data['result']
        orderbook_bids = pd.DataFrame(orderbook['bids'])
        orderbook_asks = pd.DataFrame(orderbook['asks'])
        orderbook_bids.columns = ['price', 'volume']
        orderbook_asks.columns = ['price', 'volume']
        orderbook_bids.sort_values(by='price', ascending=False)
        return (orderbook_bids, orderbook_asks)
