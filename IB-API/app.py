# Import required libraries
import time
import threading
from typing import Dict
import pandas as pd
import warnings

# Import IB API functions
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.common import BarData

# Ignore warnings
warnings.filterwarnings("ignore")

# Class for Application
class App(EClient, EWrapper):

    def __init__(self) -> None:
        EClient.__init__(self, self)
        self.data: Dict[int, pd.DataFrame] = {}
    
    def error(self, request_id: int, error_code: int, error_string: str) -> None:
        print(F"Error: {request_id}, {error_code}, {error_string}")

    def get_historical_data(self, request_id: int, contract: Contract) -> pd.DataFrame:
        self.data[request_id] = pd.DataFrame(columns=["time", "high", "low", "close"])
        self.data[request_id].set_index("time", inplace=True)
        self.reqHistoricalData(
            reqId=request_id,
            contract=contract,
            endDateTime="",
            durationStr="1 D",
            barSizeSetting="1 min",
            whatToShow="MIDPOINT",
            useRTH=0,
            formatDate=2,
            keepUpToDate=False,
            chartOptions=[],
        )
        time.sleep(3)
        return self.data[request_id]
    
    def historicalData(self, request_id: int, bar: BarData) -> None:
        df = self.data[request_id]
        df.loc[
            pd.to_datetime(bar.date, unit="s"),
            ["high", "low", "close"]
        ] = [bar.high, bar.low, bar.close]
        df = df.astype(float)
        self.data[request_id] = df

    @staticmethod
    def get_stock_contract(symbol: str) -> Contract:
        contract = Contract()
        contract.symbol = symbol
        contract.secType = "STK"
        contract.exchange = "SMART"
        contract.currency = "USD"
        return contract

# Run the application
if __name__ == "__main__":
    # Run the application
    app = App()
    app.connect("127.0.0.1", 7497, clientId=5)
    threading.Thread(target=app.run, daemon=True).start()
    # Try getting a NVDA Stock Contract
    nvda = app.get_stock_contract("AAPL")
    # Try getting historical data
    data = app.get_historical_data(99, nvda)
    print(data)
