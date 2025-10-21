"""データベース接続テスト"""
import pymysql
from dotenv import load_dotenv
import os
import ssl

load_dotenv()

print("=== データベース接続テスト ===")
print(f"Host: {os.getenv('DB_HOST')}")
print(f"Port: {os.getenv('DB_PORT')}")
print(f"User: {os.getenv('DB_USER')}")
print(f"Database: {os.getenv('DB_NAME')}")
print()

# SSL設定（Azure MySQLの場合）
db_host = os.getenv('DB_HOST')
ssl_config = None
if 'azure.com' in db_host:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    ssl_config = ssl_context
    print("✓ SSL接続を使用します")
    print()

try:
    connection = pymysql.connect(
        host=db_host,
        port=int(os.getenv('DB_PORT', 3306)),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        charset='utf8mb4',
        ssl=ssl_config
    )
    print("✅ 接続成功！")

    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM product_master")
        count = cursor.fetchone()[0]
        print(f"✅ 商品マスタのレコード数: {count}件")

        cursor.execute("SELECT CODE, NAME, PRICE FROM product_master LIMIT 3")
        products = cursor.fetchall()
        print("\n✅ サンプル商品:")
        for product in products:
            print(f"   - {product[0]}: {product[1]} ({product[2]}円)")

    connection.close()
    print("\n✅ すべてのテストが成功しました！")

except Exception as e:
    print(f"❌ エラー: {e}")
    print("\n解決方法:")
    print("1. MySQLサービスが起動しているか確認")
    print("2. .envファイルの設定を確認")
    print("3. MySQL Workbenchの接続設定と同じ値を使用")