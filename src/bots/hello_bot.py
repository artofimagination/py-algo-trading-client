from bots.bot_base import Mode, BotBase


## Exmaple trade bot for tutorial purposes.
# It is suggested to use, the following basic structure
# when writing your own bot.
# When creating your custom bot, just copy this over and rename the class
# to your desired name
class HelloBot(BotBase):
    def __init__(self, platforms, mode=Mode.Test):
        super(HelloBot, self).__init__(platforms, mode)
        self.count = 0

    ## Implement your way of market bias detector
    #  This example will switch bias every cycle.
    def _determine_bias(self):
        self.count += 1
        if self.count % 2 == 1:
            return 'bullish'
        return 'bearish'

    ## This function should do the main trading logic.
    def _trade(self):
        market_value = self.get_current_price()
        current_balance = self.get_balances()['USD']['total']
        amount_to_trade_USD = current_balance / 10
        market_structure = self._determine_bias()
        if market_structure == 'bullish':
            order_result = self.place_order(
                type='market',
                side='sell',
                price=market_value,
                volume=amount_to_trade_USD / market_value)
        elif market_structure == 'bearish':
            order_result = self.place_order(
                type='market',
                side='buy',
                price=market_value,
                volume=amount_to_trade_USD / market_value)

        if order_result is None:
            # Order failed. Balance has not enough free amount'
            pass
        return True

    # Load your test data set or any local variables, members if needed.
    def _setup(self):
        self.count = 0
        # Setup the main loop with an initial evaluation.
        (running, timestamp) = self.evaluate(self._trade)
        # Optional: Setup plot data
        self.init_plot_data()

    ## Main loop of the algorithm
    def run(self):
        try:
            self._setup()
            # Main loop of the algorithm
            while True:
                ##########################
                # Each iteration the platform will evaluate tasks
                # (For example getting the current test data,
                # or getting current market, in production mode).
                # Custom trading logic, put your decision making within _trade()
                (running, timestamp) = self.evaluate(self._trade)
                if not running:
                    break
                ##########################

                ##########################
                # Optional: statistical data for plotting in a
                # configurable window of interest.
                # Following data can be displayed:
                # Balance in case the inital balance was traded
                # once at the beginning then traded back at the end
                # BalanceIfTradedOnce = 0x0001
                # Start balance
                # StartBalance = 0x0002
                # Cumulative quote currency value of all wallets
                # BalanceCumulative = 0x0004
                # Quote currency wallet total
                # QuoteCurrencyTotal = 0x0008
                # Quote currency traded amount within time window
                # QuoteCurrencyInTimeWindow = 0x0010
                # Quote currency free amount
                # QuoteCurrencyFree = 0x0020
                # Base currency traded amount within time window
                # BaseCurrencyBalanceInWindow = 0x0040
                # Base currency total amount.
                # BaseCurrencyTotal = 0x0080
                # Base currency free amount.
                # BaseCurrencyFree = 0x0100
                # Candle price history
                # Candles = 0x0200
                self.accumulate_plot_data(timestamp, window_of_interest_seconds=15)
                ##########################

                ##########################
                # Doing platform client related cleanup if there is any.
                # Always keep this at the end of the loop, like in this example
                self.cleanup_iteration()
                ##########################
        except KeyboardInterrupt:
            pass
        # Optional: Once the simulation loop is done
        # Plot the accumulated data.
        self.plot_data(timestamp)
