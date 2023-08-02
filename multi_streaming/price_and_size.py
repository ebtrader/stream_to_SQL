import mysql.connector
import yfinance as yf
from datetime import datetime, timedelta
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
# types
from ibapi.common import *  # @UnusedWildImport
from ibapi.contract import * # @UnusedWildImport
from ibapi.ticktype import *
import time

NUMBER_OF_STRIKES = 5
TICKER = 'TQQQ'

class TestApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.contract = Contract()
        self.ticker = TICKER

    def nextValidId(self, orderId: int):
        # we can start now
        self.start()

    def start(self):
        self.tickDataOperations_req()
        print("Executing requests ... finished")

    def getDBConnection(self):
        try:
            connection = mysql.connector.connect(host='localhost',
                                                 database='javeddb',
                                                 user='root',
                                                 password='suite203',
                                                auth_plugin='mysql_native_password')
            return connection

        except mysql.connector.Error as error:
            print("Failed to connect to DB {}".format(error))
            if (connection.is_connected()):
                connection.close()
                print("MySQL connection is closed")

    def insertData(self, values, table_name):
        try:
            connection = self.getDBConnection()
            cursor = connection.cursor(prepared=True)

            if table_name == "options1":
                mySql_insert_query = """INSERT INTO options1 (ReqId, TickType, Price) 
                                       VALUES (%s, %s, %s) """
            elif table_name == "options2":
                mySql_insert_query = """INSERT INTO options2 (ReqId, TickType, Size) 
                                       VALUES (%s, %s, %s) """
            else:
                raise ValueError("Invalid table name provided.")

            # Check if values is a single value or a list/tuple of values
            if isinstance(values[0], (list, tuple)):
                cursor.executemany(mySql_insert_query, values)
            else:
                cursor.execute(mySql_insert_query, values)

            connection.commit()
            cursor.close()

        except mysql.connector.Error as error:
            print("Failed to insert record into database: {}".format(error))

        finally:
            if connection.is_connected():
                connection.close()

    def tickDataOperations_req(self):
        self.contract.symbol = self.ticker
        self.contract.secType = "OPT"
        self.contract.exchange = "SMART"
        self.contract.currency = "USD"
        self.contract.right = "C"
        self.contract.multiplier = "100"

        # Get Expiration Date of Upcoming Friday
        ticker = yf.Ticker(TICKER)
        options = ticker.options
        today = datetime.today()
        nearest_date = min(options, key=lambda x: abs(today - datetime.strptime(x, "%Y-%m-%d")))
        options_chain = ticker.option_chain(nearest_date)
        nearest_date = datetime.strptime(nearest_date, "%Y-%m-%d").strftime("%Y%m%d")  # Convert to the required format

        self.contract.lastTradeDateOrContractMonth = nearest_date

        # Get List of Strikes
        strikes = options_chain.calls.strike.tolist()

        # Get current market price
        prices = ticker.history(period='2d', interval="5m")["Close"]

        if prices.empty:
            print("No price data found for the specified date range.")
            exit()

        current_price = prices.iloc[-1]  # Get the last entry (today's closing price)
        print(prices)
        print('current price:')
        print(current_price)

        # Find the closest strikes to the current market price
        num_strikes_to_add = NUMBER_OF_STRIKES
        filtered_strikes = sorted(strikes, key=lambda x: abs(x - current_price))[:num_strikes_to_add]
        time.sleep(3)

        for strike in filtered_strikes:
            req_id = int(strike * 100)  # Example formula to create reqId
            self.contract.strike = strike
            self.reqMktData(req_id, self.contract, '', False, False, [])

    def tickPrice(self, reqId: TickerId, tickType: TickType, price: float, attrib: TickAttrib):
        super().tickPrice(reqId, tickType, price, attrib)
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
        print("TickPrice. TickerId:", reqId, "tickType:", tickType,
              "Price:", price, "CanAutoExecute:", attrib.canAutoExecute,
              "PastLimit:", attrib.pastLimit, end=' ')
        if tickType == TickTypeEnum.BID or tickType == TickTypeEnum.ASK:
            print("PreOpen:", attrib.preOpen)
        else:
            print()
        values = [(reqId, tickType, price)]  # Wrap the single value in a list
        self.insertData(values, "options1")

    def tickSize(self, reqId: TickerId, tickType: TickType, size: float):
        super().tickSize(reqId, tickType, size)
        print("TickSize. TickerId:", reqId, "TickType:", tickType, "Size: ", size)
        values = [(reqId, tickType, size)]  # Wrap the single value in a list
        self.insertData(values, "options2")

def main():
    app = TestApp()
    app.connect("127.0.0.1", port=4002, clientId=110)
    print("serverVersion:%s connectionTime:%s" % (app.serverVersion(), app.twsConnectionTime()))
    app.run()

if __name__ == "__main__":
    main()
