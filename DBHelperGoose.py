import argparse
import base64

import mysql.connector # do mysql-connector python, not the one without python
from pandas import DataFrame
from xlrd.formatting import Format

from ibapi.client import EClient
# types
from ibapi.common import *  # @UnusedWildImport
from ibapi.utils import iswrapper
from ibapi.wrapper import EWrapper

from datetime import datetime

# ! [socket_init]
class DBHelper(EWrapper, EClient):
    def __init__(self):
        EWrapper.__init__(self)
        EClient.__init__(self, wrapper=self)

    @iswrapper
    # ! [error]
    def error(self, reqId: TickerId, errorCode: int, errorString: str):
        super().error(reqId, errorCode, errorString)
        print("Error. Id:", reqId, "Code:", errorCode, "Msg:", errorString)
        errormsg = "IB error id %d errorcode %d string %s" % (reqId, errorCode, errorString)
        self._my_errors = errormsg


    def getDBConnection(self):

        try:
            connection = mysql.connector.connect(host='localhost',
                                                 database='javeddb',
                                                 user='root',
                                                 password='suite203',
                                                 auth_plugin='mysql_native_password'
                                                 )

            #print("Connection Established with DB")
            return connection

        except mysql.connector.Error as error:
            print("Failed to connect to DB {}".format(error))
            if (connection.is_connected()):
                connection.close()
                print("MySQL connection is closed")

        # finally:
        #     print("db connection finally")
        #     if (connection.is_connected()):
        #         connection.close()
        #         print("MySQL connection is closed")


    def insertData(self, values):

        try:
            connection = self.getDBConnection()
            #print("I am on line 61")
            mySql_insert_query = """INSERT INTO updatemarketdepth (ReqId, POSITION, Operation, Side, Price, SIZE, timestamp) 
                                   VALUES (%s, %s, %s, %s, %s, %s, %s) """

            cursor = connection.cursor(prepared=True)
            cursor.execute(mySql_insert_query, values)
            connection.commit()
            #print(cursor.rowcount, "Record inserted successfully into tick_by_tick_all_last table")
            cursor.close()


        except mysql.connector.Error as error:
            #print("Failed to insert record into tick_by_tick_all_last table {}".format(error))
            print("Failed to insert record into updatemarketdepth")
        finally:
            if (connection.is_connected()):
                connection.close()
                #print("MySQL connection is closed")

    def getData(self):

        try:
            connection = self.getDBConnection()
            sql_select_query = """SELECT * FROM tick_377 """

            cursor = connection.cursor(prepared=True)
            cursor.execute(sql_select_query)
            records = cursor.fetchall()
            print("Total number of rows in the time range is : ", cursor.rowcount)

            #print("\nPrinting each tick record"), , , , price, tick_size, other_attributes
            for row in records:
                print("ticker_id = ", row[1], )
                print("ticker_name = ", row[2])
                print("transaction_id  = ", row[3])
                print("price = ", row[4], )
                print("tick_size = ", row[5])
                print("other_attributes  = ", row[6])
                print("time  = ", row[8], "\n")
            #print(cursor.rowcount, "Record inserted successfully into tick_by_tick_all_last table")
            val = records
            cursor.close()
            return val

        except mysql.connector.Error as error:
            print("Failed to select record from tick_by_tick_all_last table {}".format(error))

        finally:
            if (connection.is_connected()):
                connection.close()
                #print("MySQL connection is closed")

    def getDataInPandaDF(self):

        try:
            connection = self.getDBConnection()
            sql_select_query = """SELECT * FROM tick_377 """

            cursor = connection.cursor(prepared=True)
            cursor.execute(sql_select_query)

            df = DataFrame(cursor.fetchall())
            df.columns = cursor.column_names
            print(df.head())

            return df

        except mysql.connector.Error as error:
            print("Failed to select record from tick_by_tick_all_last table {}".format(error))

        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()

    def getDeltaInPandaDF(self, value):

        try:
            connection = self.getDBConnection()
            sql_select_query = """SELECT t.id, price, tick_size, time 
 FROM tick_by_tick_all_last AS t 
INNER JOIN (SELECT id FROM tick_by_tick_all_last where id mod 377 = 0 ORDER BY id DESC Limit %s) as t2
ON t.id = t2.id
ORDER BY t.id ASC
"""
            cursor = connection.cursor(buffered=True)
            cursor.execute(sql_select_query, (value,))

            df = DataFrame(cursor.fetchall())
            if df.size!=0:
                df.columns = cursor.column_names
                #print(df)

            return df

        except mysql.connector.Error as error:
            print("Failed to select record from tick_by_tick_all_last table {}".format(error))

        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()

def main():

    app = DBHelper()
    #app.getDataInPandaDF()
    #app.getData()
    app.getDeltaInPandaDF(445614)

if __name__ == "__main__":
    main()