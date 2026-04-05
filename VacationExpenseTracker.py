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
    """Display main menu & get users choice on actions"""

    print("\nWelcome to the Vacation Expense Tracker\nPlease select which actions you would like to do" + "="*55)
    print("""1. Create new trip
          2. Work on existing trip
          3. Exit""")
    selection = input("Enter choice (1, 2, 3): ")
    return selection

def new_trip():
    """Creating a new trip"""

    print("\nBeginning a new trip is exciting!\nLet's start with some details about your trip")
    trip_name = input("Please name your trip, make sure to remember this: ")
    home_currency = input("Please enter your home currency (e.g., CAD): ").upper()
    trip_currency = input("Please enter the currency used on your trip (e.g., EUR): ").upper()
    budget = input("Please enter your trip budget (in home currency): ")

    print("\nThank you! Now let's get started on your first expense")
    amount = float(input(f"Enter expense amount (in ${trip_currency}): " ))
    category = input("Enter category for spending (food, stay, transport, event): ")
    



def main():
    """Main program loop"""

if __name__ == "__main__":
    main()