import mysql.connector
import logging
import datetime

from ibapi.contract import Contract

from ibapi.ticktype import TickType, TickTypeEnum
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.utils import iswrapper
# types
from ibapi.common import *  # @UnusedWildImport

# ! [socket_init]
class TestApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        self.contract = Contract()

    def nextValidId(self, orderId: int):
        # we can start now
        self.start()

    def start(self):
        self.tickDataOperations_req()
        print("Executing requests ... finished")

    # @printWhenExecuting
    def tickDataOperations_req(self):
        # Create contract object

        self.contract.symbol = 'NQ'
        self.contract.secType = 'FUT'
        self.contract.exchange = 'CME'
        self.contract.currency = 'USD'
        self.contract.lastTradeDateOrContractMonth = "202209"

        self.reqTickByTickData(19002, self.contract, "AllLast", 0, False)

    def tickByTickAllLast(self, reqId: int, tickType: int, time: int, price: float,
                          size: int, tickAttribLast: TickAttribLast, exchange: str,
                          specialConditions: str):
        super().tickByTickAllLast(reqId, tickType, time, price, size, tickAttribLast,
                                  exchange, specialConditions)
        if tickType == 1:
            print("Last.", end='')
        else:
            print("AllLast.", end='')
        print(" ReqId:", reqId,
              "Time:", datetime.datetime.fromtimestamp(time).strftime("%Y%m%d %H:%M:%S"),
              "Price:", price, "Size:", size,
              tickAttribLast.unreported)
        self.persistData(reqId, time, price,
                         size, tickAttribLast)

    def persistData(self, reqId: int, time: int, price: float,
                          size: int, tickAttribLast: TickAttribLast):

        values = (1,self.contract.symbol, reqId, time, price, size)

        self.insertData(values)

    def getDBConnection(self):

        path3 = 'C:/Users/jsidd/PycharmProjects/text_files/word.txt'
        with open(path3) as j:
            word = j.read()

        try:
            connection = mysql.connector.connect(host='localhost',
                                                 database='javeddb',
                                                 user='root',
                                                 password=word,
                                                 auth_plugin='mysql_native_password')

            # print("Connection Established with DB")
            return connection

        except mysql.connector.Error as error:
            print("Failed to connect to DB {}".format(error))
            if (connection.is_connected()):
                connection.close()
                print("MySQL connection is closed")

    def insertData(self, values):

        try:
            connection = self.getDBConnection()
            mySql_insert_query = """INSERT INTO tick_by_tick_all_last (ticker_id, ticker_name, transaction_id, time, 
            price, tick_size) 
            VALUES (%s, %s, %s, %s, %s, %s) """

            cursor = connection.cursor(prepared=True)
            cursor.execute(mySql_insert_query, values)
            connection.commit()
            # print(cursor.rowcount, "Record inserted successfully into tick_by_tick_all_last table")
            cursor.close()

        except mysql.connector.Error as error:
            print("Failed to insert record into tick_by_tick_all_last table {}".format(error))

        finally:
            if (connection.is_connected()):
                connection.close()
                # print("MySQL connection is closed")


def main():
    logging.getLogger().setLevel(logging.ERROR)
    app = TestApp()
    app.connect("127.0.0.1", 7497, clientId=5)
    print("serverVersion:%s connectionTime:%s" % (app.serverVersion(),
                                                  app.twsConnectionTime()))
    app.run()

if __name__ == "__main__":
    main()