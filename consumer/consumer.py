import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="fraud_db"
)

cursor = conn.cursor()

insert_query = """
INSERT INTO fraud_transactions VALUES (%s, %s, %s, ..., %s)
"""

cursor.execute(insert_query, tuple(data.values()))
conn.commit()

