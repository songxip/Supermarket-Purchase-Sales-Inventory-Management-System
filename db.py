# db.py
import psycopg

def get_conn():
    return psycopg.connect(
        host="192.168.87.129",
        port="26000",
        user="remote_user",
        password="替换为实际密码",
        dbname="supermarket_db"
    )
