from sshtunnel import SSHTunnelForwarder
import pymysql
import pandas as pd
from sqlalchemy import create_engine

# https://gist.github.com/riddhi89/9d53140dec7c17e63e22a0b5ab43f99f
# https://www.linkedin.com/pulse/programmatically-access-private-rds-database-aws-from-tom-reid/

with SSHTunnelForwarder(

        ('ec2-54-237-18-92.compute-1.amazonaws.com'),
        ssh_username='ubuntu',
        ssh_pkey=r'C:\Users\jsidd\Documents\aws\test_key.pem',
        remote_bind_address=('database-1.c3dig9vjwrmk.us-east-1.rds.amazonaws.com', 3306)

) as tunnel:
    print("****SSH Tunnel Established****")

    username = 'admin'
    hostname = '127.0.0.1'
    pwd = 'suite203'
    dbname = 'javeddb'
    port = tunnel.local_bind_port

    connection_string = 'mysql+mysqlconnector://' + username + ':' + pwd + '@' + hostname + ':' + str(port) + '/' + dbname
    engine = create_engine(connection_string)

    df = pd.read_csv('testdata.csv')
    print(df)
    df.to_sql('cloudy', con=engine, if_exists='append', index=True)
