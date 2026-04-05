#!/usr/bin/env python3

import requests
import psycopg2

# API initialization
url = "https://api.exchangerate-api.com/v4/latest/USD"
response = requests.get(url)
data = response.json()

# DB connection initialization
def connect_db():
    connection = psycopg2.connect(
        port=57243,
        host="nozomi.proxy.rlwy.net",
        database="railway",
        user="postgres",
        password="XyAdHvqeHsmnZGekmMqQpagTzHVSJeSf"
    )
    return connection

def main_menu():
    print("Welcome to the Vacation Expense Tracker \nWould you like to create a new trip or go to existing trip?\n"+"="*55)


def main():
    "Main program loop"

if __name__ == "__main__":
    main()