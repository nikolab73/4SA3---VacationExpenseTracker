#!/usr/bin/env python3

import requests
import psycopg2
from datetime import date

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



def new_trip(connection, cursor, exchange_proxy):
    """Creating a new trip"""

    #adding trip details
    print("\nBeginning a new trip is exciting!\nLet's start with some details about your trip")
    trip_name = input("Please name your trip, make sure to remember this: ")
    home_currency = input("Please enter your home currency (e.g., CAD): ").upper()
    trip_currency = input("Please enter the currency used on your trip (e.g., EUR): ").upper()
    budget = float(input("Please enter your trip budget (in home currency): "))

    # adding expense details
    print("\nThank you! Now let's get started on your first expense")
    amount = float(input(f"Enter expense amount (in {trip_currency}): " ))
    category = input("Enter category for spending (food, stay, transport, event, other): ").lower()

    # calculate converted amounts
    if home_currency != trip_currency:
        rate = exchange_proxy.get_rate(trip_currency, home_currency)
        amount_converted = amount*rate
    else:
        amount_converted = amount

    # append 1st entry to db
    cursor.execute("""INSERT INTO expenses
                   (trip_name, home_currency, trip_currency, trip_budget, amount, amount_converted, category, expense_date)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                   """, (trip_name, home_currency, trip_currency, budget, amount, amount_converted, category, date.today()))
    connection.commit()
    print(f"Trip: {trip_name} created, with first expense recorded")



def find_existing_trips(cursor):
    """Find and return existing trip"""

    # ask for trip name
    name = input("\nLet's find your trip, please enter the name: ")

    cursor.execute("SELECT * FROM expenses WHERE trip_name = %s", (name,))
    results = cursor.fetchall() # get all rows (full vacation log)

    if results:
        print(f"Found trip {name}")
        return results
    else:
        print(f"Could not find trip {name}")
        return None
    



def edit_trip_expenses(trips, connection, cursor, exchange_proxy):
    """Here the user can create, edit, delete expenses or generate report"""

    # list trip managemnet options
    print("""\nPlease select what you would like to do for this trip
          1. Create new expense
          2. Edit expense
          3. Remove expense
          4. Generate vacation report""")
    selection = input("Enter choice (1, 2, 3, 4): ")

    if selection == '1':
        add_expense(trips, connection, cursor, exchange_proxy)
    elif selection == '2':
        edit_expense(trips, connection, cursor, exchange_proxy)
    elif selection == '3':
        delete_expense(trips, connection, cursor)
    elif selection == '4':
        generate_report(trips)
    else:
        print("invalid entry")




def add_expense(trips, connection, cursor, exchange_proxy):
    """Add expense to trip"""

    # get trip info
    trip_name = trips[0][7]
    home_currency = trips[0][5]
    trip_currency = trips[0][6]
    budget = trips[0][8]

    # get expense details
    print("\nLet's add an expense")
    amount = float(input(f"Enter expense amount (in {trip_currency}): " ))
    category = input("Enter category for spending (food, stay, transport, event, other): ").lower()

    new_expense = expense_factory(category, amount, trip_currency)

    # calculate converted amounts
    if home_currency != trip_currency:
        rate = exchange_proxy.get_rate(trip_currency, home_currency)
        amount_converted = new_expense['amount']*rate
    else:
        amount_converted = new_expense['amount']

    cursor.execute("""INSERT INTO expenses
                   (trip_name, home_currency, trip_currency, trip_budget, 
                    amount, amount_converted, category, expense_date)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                   """, (trip_name, home_currency, trip_currency, budget,
                         new_expense['amount'], amount_converted, 
                         new_expense['category'], date.today()))
    
    connection.commit()
    print(f"Added {new_expense['category']} expense to {trip_name}")

def expense_factory(category, amount, trip_currency):
    """Expense factory function: creates different types of expenses based on category"""
    
    if category == "food":
        return {
            "category": "food",
            "amount": amount,
            "currency": trip_currency,
        }
    elif category == "stay":
        return {
            "category": "stay",
            "amount": amount,
            "currency": trip_currency,
        }
    elif category == "transport":
        return {
            "category": "transport",
            "amount": amount,
            "currency": trip_currency,
        }
    elif category == "event":
        return {
            "category": "event",
            "amount": amount,
            "currency": trip_currency,
        }
    else:
        return {
            "category": "other",
            "amount": amount,
            "currency": trip_currency,
        }



def edit_expense(trips, connection, cursor, exchange_proxy):
    """Edit existing entry in table"""

    trip_name = trips[0][7]
    home_currency = trips[0][5]
    trip_currency = trips[0][6]
    
    print(f"\nShowing expenses for {trip_name}" + "-"*55)
    for i, expense in enumerate(trips):
        expense_id = expense[0]
        category = expense[1]
        date = expense[2]
        amount = expense[3]
        print(f"ID: {expense_id}, Category: {category}, Amount: {amount}{trip_currency}, Dated: {date}")
    
    choice = int(input("Enter ID # of expense you would like to edit"))
    amount = float(input(f"Enter new expense amount (in {trip_currency}): " ))
    category = input("Enter category for spending (food, stay, transport, event, other): ").lower()

    # calculate converted amounts
    if home_currency != trip_currency:
        rate = exchange_proxy.get_rate(trip_currency, home_currency)
        amount_converted = amount*rate
    else:
        amount_converted = amount

    cursor.execute("""UPDATE expenses 
                   SET amount = %s, amount_converted = %s, category = %s 
                   WHERE expense_id = %s
                   """, (amount, amount_converted, category, choice))
    connection.commit()

    print(f"\nUpdated expense ID: {choice}")

    


def delete_expense(trips, connection, cursor):
    """Remove entry from table"""

    trip_name = trips[0][7]
    
    print(f"\nShowing expenses for {trip_name}" + "-"*55)
    for i, expense in enumerate(trips):
        expense_id = expense[0]
        category = expense[1]
        date = expense[2]
        amount = expense[3]
        trip_currency = expense[7]
        print(f"ID: {expense_id}, Category: {category}, Amount: {amount}{trip_currency}, Dated: {date}")
    
    choice = int(input("Enter ID # of expense you would like to delete"))

    cursor.execute("DELETE FROM expenses WHERE expense_id = %s", (choice,))
    connection.commit()
    print(f"Expense removed from {trip_name}")




def generate_report(trips):
    """Generate vacation expense and budget report"""



class currency_conversion:
    """Used to convert currencies and store previous conversions using proxy pattern"""

    def __init__(self):
        self.cache = {}

    def get_rate(self, trip_currency, home_currency):
        cache_key = f"{trip_currency} to {home_currency}" # initialize cache key, conversion from trip (amount entered) to home (converted value also saved)

        # check if cached key exists
        if cache_key in self.cache: # check if the string (conversion from, to) exists in the keys
            return self.cache[cache_key] # return rate
        
        try:
            # API initialization
            url = "https://api.exchangerate-api.com/v4/latest/USD"
            response = requests.get(url)
            data = response.json()

            # if home currency is USD - exchange rates API only allows USD conversion for free so we will account for this
            if home_currency == "USD":
                rate = 1/data['rates'][trip_currency]
            # if trip currency is USD
            elif trip_currency == "USD":
                rate = data['rates'][home_currency]
            # if neither are USD
            else:
                USD_to_home = data['rates'][home_currency]
                USD_to_trip = data['rates'][trip_currency]
                rate = USD_to_home/USD_to_trip

            self.cache[cache_key] = rate # save conversion rate in cache, avoid multiple API calls
            return rate

        except:
            print("Error fetching rate")
            return 1.0
    


def main():
    """Main program loop"""

    DBconnection = connect_db()
    cursor = DBconnection.cursor()
    exchange_proxy = currency_conversion()

    while True:

        choice = main_menu()

        if choice == '1':
            new_trip(DBconnection, cursor, exchange_proxy)

        elif choice == '2':
            trips = find_existing_trips(cursor)
            edit_trip_expenses(trips, DBconnection, cursor, exchange_proxy)
        elif choice == '3':
            print("Exiting program, thank you")
            break
        else:
            print("Invalid entry")



if __name__ == "__main__":
    main()