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
cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id SERIAL PRIMARY KEY,
        amount float,
        category VARCHAR(50)
    )
""")