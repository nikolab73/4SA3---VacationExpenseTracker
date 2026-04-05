#!/usr/bin/env python3
import psycopg2

connection = psycopg2.connect(
    port=57243,
    host="nozomi.proxy.rlwy.net",
    database="railway",
    user="postgres",
    password="XyAdHvqeHsmnZGekmMqQpagTzHVSJeSf"
)

cursor = connection.cursor()

# Delete old table
cursor.execute("DROP TABLE IF EXISTS expenses")

# Create new table
cursor.execute("""
    CREATE TABLE expenses(
        expense_id SERIAL PRIMARY KEY,
        category VARCHAR(50),
        expense_date DATE,
               
        amount DECIMAL(10,2),
        amount_converted DECIMAL(10,2),
               
        home_currency VARCHAR(3),
        trip_currency VARCHAR(3),
               
        trip_name VARCHAR(100),
        trip_budget DECIMAL(10,2)
    )
""")

connection.commit()
connection.close()
print("Database table reset")