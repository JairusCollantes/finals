import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="jairus", # check if this is correct!
        database="poker"
    )
    print("Connection Successful!")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players")
    print("Players found:", cursor.fetchall())
    conn.close()
except Exception as e:
    print(f"Connection Failed: {e}")