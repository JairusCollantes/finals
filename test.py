import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()
try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        database = os.getenv("DB_NAME")
    )
    print("Connection Successful!")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players")
    print("Players found:", cursor.fetchall())
    conn.close()
except Exception as e:
    print(f"Connection Failed: {e}")