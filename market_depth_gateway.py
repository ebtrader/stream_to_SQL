import mysql.connector
import csv
import argparse
import datetime

import collections
import inspect
import logging
import os.path
import time


import pandas as pd
from datetime import datetime
from ibapi import wrapper
from ibapi import utils
from ibapi.client import EClient
from ibapi.utils import iswrapper

from ibapi.ticktype import TickType, TickTypeEnum
from ibapi import wrapper
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
# types
from ibapi.common import *  # @UnusedWildImport
from ibapi.order import *  # @UnusedWildImport

from ibapi.contract import Contract


def SetupLogger():
    if not os.path.exists("log"):
        os.makedirs("log")

    time.strftime("pyibapi.%Y%m%d_%H%M%S.log")

    recfmt = '(%(threadName)s) %(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)d %(message)s'

    timefmt = '%y%m%d_%H:%M:%S'

    # logging.basicConfig( level=logging.DEBUG,
    #                    format=recfmt, datefmt=timefmt)
    logging.basicConfig(filename=time.strftime("log/pyibapi.%y%m%d_%H%M%S.log"),
                        filemode="w",
                        level=logging.INFO,
                        format=recfmt, datefmt=timefmt)
    logger = logging.getLogger()
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logger.addHandler(console)


def printWhenExecuting(fn):
    def fn2(self):
        print("   doing", fn.__name__)
        fn(self)
        print("   done w/", fn.__name__)

    return fn2

def printinstance(inst:Object):
    attrs = vars(inst)
    print(', '.join("%s: %s" % item for item in attrs.items()))

class Activity(Object):
    def __init__(self, reqMsgId, ansMsgId, ansEndMsgId, reqId):
        self.reqMsdId = reqMsgId
        self.ansMsgId = ansMsgId
        self.ansEndMsgId = ansEndMsgId
        self.reqId = reqId


class RequestMgr(Object):
    def __init__(self):
        # I will keep this simple even if slower for now: only one list of
        # requests finding will be done by linear search
        self.requests = []

    def addReq(self, req):
        self.requests.append(req)

    def receivedMsg(self, msg):
        pass

# ! [socket_init]
class TestApp(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)
        #self.df = pd.DataFrame(columns=['reqid', 'Position', 'Operation', 'Side', 'Price', 'Size', 'Time'])
        # ! [socket_init]
        self.nKeybInt = 0
        self.started = False
        self.nextValidOrderId = None
        self.permId2ord = {}
        self.globalCancelOnly = False
        self.simplePlaceOid = None
        self._my_errors = {}
        self.contract = Contract()

    def dumpReqAnsErrSituation(self):
        logging.debug("%s\t%s\t%s\t%s" % ("ReqId", "#Req", "#Ans", "#Err"))
        for reqId in sorted(self.reqId2nReq.keys()):
            nReq = self.reqId2nReq.get(reqId, 0)
            nAns = self.reqId2nAns.get(reqId, 0)
            nErr = self.reqId2nErr.get(reqId, 0)
            logging.debug("%d\t%d\t%s\t%d" % (reqId, nReq, nAns, nErr))

    @iswrapper
    # ! [connectack]
    def connectAck(self):
        if self.asynchronous:
            self.startApi()

    # ! [connectack]

    @iswrapper
    # ! [nextvalidid]
    def nextValidId(self, orderId: int):
        super().nextValidId(orderId)

        logging.debug("setting nextValidOrderId: %d", orderId)
        self.nextValidOrderId = orderId
        print("NextValidId:", orderId)
        # ! [nextvalidid]

        # we can start now
        self.start()

    def start(self):
        if self.started:
            return

        self.started = True

        if self.globalCancelOnly:
            print("Executing GlobalCancel only")
            self.reqGlobalCancel()
        else:
            print("Executing requests")
            #self.tickDataOperations_req()
            self.marketDepthOperations_req()

            print("Executing requests ... finished")

    def keyboardInterrupt(self):
        self.nKeybInt += 1
        if self.nKeybInt == 1:
            self.stop()
        else:
            print("Finishing test")
            self.done = True

    def stop(self):
        print("Executing cancels")
        # self.orderOperations_cancel()
        # self.accountOperations_cancel()
        #self.tickDataOperations_cancel()
        self.marketDepthOperations_cancel()
        # self.realTimeBarsOperations_cancel()
        # self.historicalDataOperations_cancel()
        # self.optionsOperations_cancel()
        # self.marketScanners_cancel()
        # self.fundamentalsOperations_cancel()
        # self.bulletinsOperations_cancel()
        # self.newsOperations_cancel()
        # self.pnlOperations_cancel()
        # self.histogramOperations_cancel()
        # self.continuousFuturesOperations_cancel()
        # self.tickByTickOperations_cancel()
        print("Executing cancels ... finished")

    def nextOrderId(self):
        oid = self.nextValidOrderId
        self.nextValidOrderId += 1
        return oid

    @iswrapper
    # ! [error]
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)
        errormsg = "IB error id %d errorcode %d string %s" % (reqId, errorCode, errorString)
        self._my_errors = errormsg

    @iswrapper
    def winError(self, text: str, lastError: int):
        super().winError(text, lastError)

    def getDBConnection(self):
        try:
            connection = mysql.connector.connect(host='database-1.c3dig9vjwrmk.us-east-1.rds.amazonaws.com',
                                                 database='javeddb',
                                                 user='admin',
                                                 password='word')

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
            # print("I am on line 61")
            mySql_insert_query = """INSERT INTO updatemarketdepth (ReqId, POSITION, Operation, Side, Price, SIZE, timestamp) 
                                   VALUES (%s, %s, %s, %s, %s, %s, %s) """

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


    @printWhenExecuting
    def marketDepthOperations_req(self):
        # Requesting the Deep Book
        # ! [reqmarketdepth]
        #self.reqMktDepth(2001, ContractSamples.EurGbpFx(), 5, False, [])

        #self.reqMktDepth(2001, ContractSamples.USStock(), 5, True, [])
        self.contract.symbol = 'NQ'
        self.contract.secType = 'FUT'
        self.contract.exchange = 'CME'
        self.contract.currency = 'USD'
        self.contract.lastTradeDateOrContractMonth = "202309"

        self.reqMktDepth(2002, self.contract, 5, True, [])
        # ! [reqmarketdepth]

        # ! [reqmarketdepth]
        #self.reqMktDepth(2002, ContractSamples.EuropeanStock(), 5, True, [])
        # ! [reqmarketdepth]

        # Request list of exchanges sending market depth to UpdateMktDepthL2()
        # ! [reqMktDepthExchanges]
        # self.reqMktDepthExchanges()
        # ! [reqMktDepthExchanges]

    @printWhenExecuting
    def marketDepthOperations_cancel(self):
        # Canceling the Deep Book request
        # ! [cancelmktdepth]
        self.cancelMktDepth(2001, False)
        self.cancelMktDepth(2002, True)
        # ! [cancelmktdepth]

    @iswrapper
    # ! [updatemktdepthl2]
    def updateMktDepthL2(self, reqId: TickerId, position: int, marketMaker: str,
                         operation: int, side: int, price: float, size: int, isSmartDepth: bool):
        super().updateMktDepthL2(reqId, position, marketMaker, operation, side,
                                 price, size, isSmartDepth)
        now = datetime.now()
        timestamp = now.strftime("%d/%m/%Y %H:%M:%S")
        print("UpdateMarketDepthL2. ReqId:", reqId, "Position:", position, "Operation:",
              operation, "Side:", side, "Price:", price, "Size:", size, "Time:", timestamp)
        self.persistData(reqId, position, operation, side, price, size, timestamp)
        #self.df.loc[len(self.df)] = [reqId, position, operation, side, price, size, timestamp]
        #self.df.to_csv('program_L2.csv')
    # ! [updatemktdepthl2]

    def persistData(self, reqId: TickerId, position: int, operation: int,
                       side: int, price: float, size: int, timestamp: str):
        #print("current datetime stamp is : {}".format(datetime))


        values = (reqId, position, operation, side, price, size, timestamp)

        self.insertData(values)



def main():
    SetupLogger()
    logging.getLogger().setLevel(logging.ERROR)

    cmdLineParser = argparse.ArgumentParser("api tests")
    # cmdLineParser.add_option("-c", action="store_True", dest="use_cache", default = False, help = "use the cache")
    # cmdLineParser.add_option("-f", action="store", type="string", dest="file", default="", help="the input file")
    cmdLineParser.add_argument("-p", "--port", action="store", type=int,
                               dest="port", default=4002, help="The TCP port to use")
    cmdLineParser.add_argument("-C", "--global-cancel", action="store_true",
                               dest="global_cancel", default=False,
                               help="whether to trigger a globalCancel req")
    args = cmdLineParser.parse_args()
    print("Using args", args)
    logging.debug("Using args %s", args)
    # print(args)

    # tc = TestClient(None)
    # tc.reqMktData(1101, ContractSamples.USStockAtSmart(), "", False, None)
    # print(tc.reqId2nReq)
    # sys.exit(1)
    app = TestApp()
    try:
        if args.global_cancel:
            app.globalCancelOnly = True
        # ! [connect]
        app.connect("127.0.0.1", args.port, clientId=15)
        # ! [connect]
        print("serverVersion:%s connectionTime:%s" % (app.serverVersion(),
                                                      app.twsConnectionTime()))
        # ! [clientrun]
        app.run()
        # ! [clientrun]
    except:
        raise


if __name__ == "__main__":
    main()