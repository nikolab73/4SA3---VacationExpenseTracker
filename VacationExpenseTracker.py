#!/usr/bin/env python3

import requests
import psycopg2
from datetime import date

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



def new_trip(connection, cursor):
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
    category = input("Enter category for spending (food, stay, transport, event, other): ")

    # calculate converted amounts
    if home_currency != trip_currency:
        amount_converted = amount*1.10 # placeholder for conversion
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
    


def edit_trip_expenses(trips, connection, cursor):
    """Here the user can create, edit, delete expenses or generate report"""

    # list trip managemnet options
    print("""\nPlease select what you would like to do for this trip
          1. Create new expense
          2. Edit expense
          3. Remove expense
          4. Generate vacation report""")
    selection = input("Enter choice (1, 2, 3, 4): ")

    if selection == '1':
        add_expense(trips, connection, cursor)
    elif selection == '2':
        edit_expense(trips, connection, cursor)
    elif selection == '3':
        delete_expense(trips, connection, cursor)
    elif selection == '4':
        generate_report(trips)
    else:
        print("invalid entry")




def add_expense(trips, connection, cursor):
    """Add expense to trip"""

    # get trip info
    trip_name = trips[0][7]
    home_currency = trips[0][5]
    trip_currency = trips[0][6]
    budget = trips[0][8]

    # get expense details
    print("\nLet's add an expense")
    amount = float(input(f"Enter expense amount (in {trip_currency}): " ))
    category = input("Enter category for spending (food, stay, transport, event, other): ")

    # calculate converted amounts
    if home_currency != trip_currency:
        amount_converted = amount*1.10 # placeholder for conversion
    else:
        amount_converted = amount

    cursor.execute("""INSERT INTO expenses
                   (trip_name, home_currency, trip_currency, trip_budget, amount, amount_converted, category, expense_date)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                   """, (trip_name, home_currency, trip_currency, budget, amount, amount_converted, category, date.today()))
    connection.commit()
    print(f"Added {category} expense to {trip_name}")




def edit_expense(trips, connection, cursor):
    """Edit existing entry in table"""

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
    
    choice = input("Enter ID # of expense you would like to delete")

    cursor.execute("DELETE FROM expenses WHERE expense_id = %s", (expense_id))
    connection.commit()
    print(f"Expense removed from {trip_name}")




def generate_report(trips):
    """Generate vacation expense and budget report"""


def main():
    """Main program loop"""

    DBconnection = connect_db()
    cursor = DBconnection.cursor()

    while True:

        choice = main_menu()

        if choice == '1':
            new_trip(DBconnection, cursor)

        elif choice == '2':
            trips = find_existing_trips(cursor)
            edit_trip_expenses(trips, DBconnection, cursor)
        elif choice == '3':
            print("Exiting program, thank you")
            break
        else:
            print("Invalid entry")



if __name__ == "__main__":
    main()