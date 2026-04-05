#!/usr/bin/env python3

import requests
import psycopg2

# API initialization
url = "https://api.exchangerate-api.com/v4/latest/USD"
response = requests.get(url)
data = response.json()

# DB connection initialization
connection = psycopg2.connect(
    port=57243,
    host="nozomi.proxy.rlwy.net",
    database="railway",
    user="postgres",
    password="XyAdHvqeHsmnZGekmMqQpagTzHVSJeSf"
)

cursor = connection.cursor()

# Create table

# Drop old table if it exists
cursor.execute("DROP TABLE IF EXISTS expenses")

# Create single expenses table with trip info
cursor.execute("""
    CREATE TABLE expenses(
        expense_id SERIAL PRIMARY KEY,
        category VARCHAR(50),
        expense_date VARCHAR(50),
               
        amount DECIMAL(10,2),
        amount_converted DECIMAL(10,2),
               
        home_currency VARCHAR(3),
        trip_currency VARCHAR(3),
               
        trip_name VARCHAR(50),
        trip_budget DECIMAL(10,2)
    )
""")

# main program

print("Welcome to the Vacation Expense Tracker \nWould you like to create a new trip or ")

cursor.execute("INSERT INTO expenses (amount, category) VALUES (50.01, 'food')")

connection.commit()
connection.close()