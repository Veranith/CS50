import pathlib
import logging
import os
import mysql.connector
import ssl
from mysql.connector import errorcode
from mysql.connector.connection import MySQLConnection
from mysql.connector.constants import ClientFlag


# Validate needed Evironment varabiles are present. 
if not os.environ.get('dbUser'):
    raise ValueError("Need to define dbUser environment variable")
if not os.environ.get('dbPassword'):
    raise ValueError("Need to define dbPassword environment variable")
if not os.environ.get('dbHost'):
    raise ValueError("Need to define dbHost environment variable")
if not os.environ.get('database'):
    raise ValueError("Need to define database environment variable")


def get_ssl_cert():
    """Get path of Azure crt file"""
    current_path = pathlib.Path(__file__).parent
    return str(current_path / 'BaltimoreCyberTrustRoot.crt.pem')


def open_azure_db():
    logging.info(ssl.OPENSSL_VERSION)
    """Create Azure DB connection"""
    # https://docs.microsoft.com/en-us/azure/mysql/connect-python
    config = {
        'user': os.environ.get('dbUser'),
        'password': os.environ.get('dbPassword'),
        'host': os.environ.get('dbHost'),
        'database': os.environ.get('database'),
        'client_flags': [ClientFlag.SSL],
        'ssl_verify_cert': True,
        'ssl_ca': get_ssl_cert()
    }
    
    # Connect via TLSv1.2
    conn = MySQLConnection()
    conn._ssl['version'] = ssl.PROTOCOL_TLSv1_2
    try:
        conn = mysql.connector.connect(**config)
        logging.info("Connection established")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logging.error("Something is wrong with the user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            logging.error("Database does not exist")
        else:
            logging.error(err)
        raise Exception("Failed to connect to DB") from err
    else:
        cursor = conn.cursor(dictionary=True)

    return conn, cursor


def close_azure_db(conn, cursor):
    """Close Azure DB connection"""
    cursor.close()
    conn.close()
    logging.info("Closed DB")

