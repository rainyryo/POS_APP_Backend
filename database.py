"""データベース接続モジュール"""
import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
import os
import ssl
from dotenv import load_dotenv

load_dotenv()

# データベース設定
db_host = os.getenv('DB_HOST', 'localhost')
DB_CONFIG = {
    'host': db_host,
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'pos_db'),
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}

# Azure MySQLの場合はSSLを有効化
if 'azure.com' in db_host:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    DB_CONFIG['ssl'] = ssl_context

@contextmanager
def get_db_connection():
    """データベース接続のコンテキストマネージャー"""
    connection = pymysql.connect(**DB_CONFIG)
    try:
        yield connection
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        connection.close()

def get_cursor(connection):
    """カーソル取得"""
    return connection.cursor()