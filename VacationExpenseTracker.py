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



def new_trip(connection, cursor, exchange_proxy):
    """Creating a new trip"""

    #adding trip details
    print("\nBeginning a new trip is exciting!\nLet's start with some details about your trip")
    trip_name = input("Please name your trip, make sure to remember this: ")
    home_currency = input("Please enter your home currency (e.g., CAD, USD, EUR): ").upper()
    trip_currency = input("Please enter the currency used on your trip (e.g., EUR): ").upper()
    budget = float(input(f"Please enter your trip budget (in home currency {home_currency}): "))

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

    cursor.execute("SELECT * FROM expenses WHERE trip_name = %s", (trip_name,))
    return cursor.fetchall()
    



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
    print("\nPlease select what you would like to do for this trip")
    print("1. Create new expense")
    print("2. Edit expense")
    print("3. Remove expense")
    print("4. Generate vacation report")
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

    cursor.execute("SELECT * FROM expenses WHERE trip_name = %s", (trips[0][7],))
    return cursor.fetchall()



def add_expense(trips, connection, cursor, exchange_proxy):
    """Add expense to trip"""

    # get trip info
    trip_name = trips[0][7]
    home_currency = trips[0][5]
    trip_currency = trips[0][6]
    budget = float(trips[0][8])

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
                   (trip_name, home_currency, trip_currency, trip_budget, amount, amount_converted, category, expense_date)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                   """, (trip_name, home_currency, trip_currency, budget, new_expense['amount'], amount_converted, new_expense['category'], date.today()))
    
    connection.commit()
    print(f"Added {new_expense['category']} expense to {trip_name}")
    budget_alerts(trips, amount_converted, home_currency)

    cursor.execute("SELECT * FROM expenses WHERE trip_name = %s", (trip_name,))
    return cursor.fetchall()


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
    
    print(f"\nShowing expenses for {trip_name}\n" + "-"*55)
    for i, expense in enumerate(trips):
        expense_id = expense[0]
        category = expense[1]
        date = expense[2]
        amount = expense[3]
        print(f"ID: {expense_id}, Category: {category}, Amount: {amount}{trip_currency}, Dated: {date}")
    
    choice = int(input("Enter ID # of expense you would like to edit: "))
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
    budget_alerts(trips, amount_converted, home_currency)

    


def delete_expense(trips, connection, cursor):
    """Remove entry from table"""

    trip_name = trips[0][7]
    
    print(f"\nShowing expenses for {trip_name}\n" + "-"*55)
    for i, expense in enumerate(trips):
        expense_id = expense[0]
        category = expense[1]
        date = expense[2]
        amount = expense[3]
        trip_currency = expense[7]
        print(f"ID: {expense_id}, Category: {category}, Amount: {amount}{trip_currency}, Dated: {date}")
    
    choice = int(input("Enter ID # of expense you would like to delete: "))

    cursor.execute("DELETE FROM expenses WHERE expense_id = %s", (choice,))
    connection.commit()
    print(f"Expense removed from {trip_name}")



def generate_report(trips):
    """Generate vacation expense and budget report"""

    trip_name = trips[0][7]
    budget = float(trips[0][8])
    home_currency = trips[0][5]
    
    # add total spent on food, stay, transport, event, other
    food_cost = 0.0
    stay_cost = 0.0
    transport_cost = 0.0
    event_cost = 0.0
    other_cost = 0.0
    total_spent = 0.0

    for i, expenses in enumerate(trips): # iterate through trips to find total spent and cost per category
        amount = float(expenses[4])
        total_spent += amount

        if expenses[1] == "food": # add food costs
            food_cost += amount

        elif expenses[1] == "stay": # add stay costs
            stay_cost += amount

        elif expenses[1] == "transport": # add transport costs
            transport_cost += amount

        elif expenses[1] == "event": # add event costs
            event_cost += amount

        else: # add other costs
            other_cost += amount

    remaining = budget-total_spent
    percent_spent = total_spent/budget*100
    
    print(f"\n---------------------------- Trip Report ----------------------------\nShowing details for {trip_name}\n" + "-"*69)
    print(f"Budget: {home_currency}{budget:.2f}")
    print(f"Total Spent: {home_currency}{total_spent:.2f}")
    print(f"Remaining: {home_currency}{remaining:.2f}")
    print(f"% Spent: {percent_spent:.1f}%")
    print("\nExpenses by category:")
    print(f"Food: {home_currency}{food_cost:.2f}")
    print(f"Stay: {home_currency}{stay_cost:.2f}")
    print(f"Transportation: {home_currency}{transport_cost:.2f}")
    print(f"Events: {home_currency}{event_cost:.2f}")
    print(f"Other: {home_currency}{other_cost:.2f}")
    print("-"*69)



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
    


def budget_alerts(trips, expense, home_currency):
    """Print budget alerts to user based on budget use - partially follows strategy pattern"""

    budget = float(trips[0][8])
    target_80 = budget*0.8
    large_spend = budget*0.15
    total_spent = 0.0

    for i, expenses in enumerate(trips): # iterate through trips to find total spent
        total_spent += float(expenses[4]) 

    remaining = budget-total_spent

    if remaining < 0:
        print(f"ALERT!: Budget of {budget:.2f}{home_currency} exceeded")
        remaining = 0

    if float(expense) >= large_spend:
        print(f"ALERT!: Your expense of {expense:.2f}{home_currency} exceeds 15% of your total budget")

    if total_spent > target_80:
        print(f"ALERT!: You have exceeded 80% of your budget. Total spend = {total_spent:.2f}{home_currency}")

    if remaining <= 100:
        print(f"ALERT!: You have less than 100{home_currency:.2f} remaining. Amount remaining = {remaining:.2f}")



def main():
    """Main program loop"""

    DBconnection = connect_db()
    cursor = DBconnection.cursor()
    exchange_proxy = currency_conversion()

    current_trip = None

    print("Welcome to the Vacation Expense Tracker\n")

    while True:

        print("\nPlease select which actions you would like to do\n" + "="*55)
        print("1. Create new trip")
        print("2. Work on existing trip")
        
        if current_trip:
            print("3. Work on a different trips")
            print("4. Exit")
            print(f"\nCurrently working on: {current_trip[0][7]}")
            selection = input("Enter choice (1, 2, 3, 4): ")
        else:
            print("3. Exit")
            selection = input("Enter choice (1, 2, 3): ")

        if selection == '1':
            current_trip = new_trip(DBconnection, cursor, exchange_proxy)

        elif selection == '2':
            if current_trip:
                current_trip = edit_trip_expenses(current_trip, DBconnection, cursor, exchange_proxy)
            else:
                trips = find_existing_trips(cursor)
                current_trip = trips
                edit_trip_expenses(trips, DBconnection, cursor, exchange_proxy)
            
        elif selection == '3':
            if current_trip:
                trips = find_existing_trips(cursor)
                current_trip = trips
                edit_trip_expenses(trips, DBconnection, cursor, exchange_proxy)
            else:
                print("Exiting program, thank you")
                break
        elif selection == '4':
            if current_trip:
                print("Exiting program, thank you")
                break
        else:
            print("Invalid entry")


if __name__ == "__main__":
    main()