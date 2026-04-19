import os
import shutil
from colorama import Fore, Style, init
import json

# Initialize colorama
init(autoreset=True)

# Directory and File Setup
DATA_DIR = "data"
BACKUP_DIR = "backup"
TRAIN_FILE = os.path.join(DATA_DIR, "trains.txt")
CUSTOMER_FILE = os.path.join(DATA_DIR, "customers.txt")
RESERVATION_FILE = os.path.join(DATA_DIR, "reservations.txt")

# Utility Functions
def setup_environment():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(BACKUP_DIR, exist_ok=True)
    for file in [TRAIN_FILE, CUSTOMER_FILE, RESERVATION_FILE]:
        if not os.path.exists(file):
            open(file, 'w').close()

def colorful_message(message, color=Fore.CYAN, style=Style.BRIGHT):
    print(f"{color}{style}{message}")

# File Operations

def load_file(file_path):
    try:
        with open(file_path, 'r') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        open(file_path, 'w').close()
        return []

def save_file(file_path, data):
    with open(file_path, 'w') as file:
        for line in data:
            file.write(line + '\n')

# Train Management
def load_trains():
    trains = []
    for t in load_file(TRAIN_FILE):
        fields = t.split('|')
        if len(fields) == 5:
            trains.append({
                "id": fields[0],
                "name": fields[1],
                "schedule": fields[2],
                "route": fields[3],
                "available_seats": fields[4]
            })
        else:
            colorful_message(f"Skipping malformed train entry: {t}", Fore.YELLOW)
    return trains

def save_trains(trains):
    save_file(TRAIN_FILE, ["|".join(t.values()) for t in trains])

def add_train():
    colorful_message("\n=== Add Train ===", Fore.YELLOW)
    trains = load_trains()
    train_id = input(Fore.CYAN + "Enter Train ID: ").strip()
    if any(train["id"] == train_id for train in trains):
        colorful_message("Train ID already exists.", Fore.RED)
        return
    name = input(Fore.CYAN + "Enter Train Name: ").strip()
    schedule = input(Fore.CYAN + "Enter Train Schedule: ").strip()
    route = input(Fore.CYAN + "Enter Train Route: ").strip()
    seats = input(Fore.CYAN + "Enter Available Seats: ").strip()
    trains.append({"id": train_id, "name": name, "schedule": schedule, "route": route, "available_seats": seats})
    save_trains(trains)
    colorful_message("Train added successfully!", Fore.GREEN)

def view_trains():
    trains = load_trains()
    if trains:
        colorful_message("\n=== Available Trains ===", Fore.YELLOW)
        for train in trains:
            print(Fore.CYAN + f"ID: {train['id']} | Name: {train['name']} | Schedule: {train['schedule']} | Route: {train['route']} | Seats: {train['available_seats']}")
    else:
        colorful_message("No trains available.", Fore.RED)

# Reservation Management
def load_reservations():
    return [dict(zip(["id", "customer_id", "train_id", "seats"], r.split('|'))) for r in load_file(RESERVATION_FILE)]

def save_reservations(reservations):
    save_file(RESERVATION_FILE, ["|".join(r.values()) for r in reservations])

def book_ticket(customer_id):
    trains = load_trains()
    if not trains:
        colorful_message("No trains available for booking.", Fore.RED)
        return
    view_trains()
    train_id = input(Fore.CYAN + "Enter Train ID to book: ").strip()
    selected_train = next((train for train in trains if train["id"] == train_id), None)
    if not selected_train:
        colorful_message("Invalid Train ID.", Fore.RED)
        return
    seats = int(input(Fore.CYAN + "Enter number of seats to book: ").strip())
    available_seats = int(selected_train["available_seats"])
    if seats > available_seats:
        colorful_message("Not enough seats available.", Fore.RED)
        return
    selected_train["available_seats"] = str(available_seats - seats)
    save_trains(trains)
    reservations = load_reservations()
    reservation_id = str(len(reservations) + 1)
    reservations.append({"id": reservation_id, "customer_id": customer_id, "train_id": train_id, "seats": str(seats)})
    save_reservations(reservations)
    colorful_message("Ticket booked successfully!", Fore.GREEN)

def cancel_reservation(customer_id):
    reservations = load_reservations()
    trains = load_trains()
    reservation_id = input(Fore.CYAN + "Enter Reservation ID: ").strip()
    reservation = next((r for r in reservations if r["id"] == reservation_id and r["customer_id"] == customer_id), None)
    if not reservation:
        colorful_message("Reservation not found.", Fore.RED)
        return
    reservations.remove(reservation)
    for train in trains:
        if train["id"] == reservation["train_id"]:
            train["available_seats"] = str(int(train["available_seats"]) + int(reservation["seats"]))
            break
    save_reservations(reservations)
    save_trains(trains)
    colorful_message("Reservation canceled successfully!", Fore.GREEN)

# Customer Management
def load_customers():
    try:
        # Check if the file exists
        if not os.path.exists("customers.json"):
            # Create an empty file if it doesn't exist
            with open("customers.json", "w") as file:
                json.dump([], file)  # Initialize with an empty list
            print("customers.json file created.")

        with open("customers.json", "r") as file:
            return json.load(file)

    except json.JSONDecodeError:
        print("Error decoding customers.json. Returning an empty list.")
        return []
def add_customer(customer_id, name, email):
    customers = load_customers()
    customers.append({"id": customer_id, "name": name, "email": email})
    save_customers(customers)
    print(f"Customer {name} added successfully.")

def save_customers(customers):
    try:
        with open("customers.json", "w") as file:
            json.dump(customers, file, indent=4)
        print("Customers successfully saved.")
    except Exception as e:
        print(f"An error occurred while saving customers: {e}")

def register_customer():
    colorful_message("\n=== Register Customer ===", Fore.YELLOW)
    customers = load_customers()
    customer_id = input(Fore.CYAN + "Enter Customer ID: ").strip()
    if any(c["id"] == customer_id for c in customers):
        colorful_message("Customer ID already exists.", Fore.RED)
        return
    name = input(Fore.CYAN + "Enter Customer Name: ").strip()
    password = input(Fore.CYAN + "Enter Password: ").strip()
    customers.append({"id": customer_id, "name": name, "password": password})
    save_customers(customers)
    colorful_message("Customer registered successfully!", Fore.GREEN)

def login_customer():
    colorful_message("\n=== Customer Login ===", Fore.YELLOW)
    customers = load_customers()
    customer_id = input(Fore.CYAN + "Enter Customer ID: ").strip()
    password = input(Fore.CYAN + "Enter Password: ").strip()
    customer = next((c for c in customers if c["id"] == customer_id and c["password"] == password), None)
    if customer:
        colorful_message("Login successful!", Fore.GREEN)
        customer_menu(customer_id)
    else:
        colorful_message("Account Not Found, Register First.", Fore.RED)

def view_customers():
    """Displays a list of all registered customers."""
    customers = load_customers()
    if customers:
        colorful_message("\n=== Registered Customers ===", Fore.YELLOW)
        for customer in customers:
            print(Fore.CYAN + f"ID: {customer['id']} | Name: {customer['name']} | Password: {customer['password']}")
    else:
        colorful_message("No customers found.", Fore.RED)

def delete_customer():
    """Allows admin to delete a customer by ID."""
    customers = load_customers()
    if not customers:
        colorful_message("No customers found.", Fore.RED)
        return

    view_customers()  # Display all customers for reference
    customer_id = input(Fore.CYAN + "Enter the Customer ID to delete: ").strip()

    # Find the customer by ID
    for customer in customers:
        if customer["id"] == customer_id:
            customers.remove(customer)
            save_customers(customers)
            colorful_message(f"Customer with ID {customer_id} has been deleted.", Fore.GREEN)
            return

    colorful_message(f"Customer with ID {customer_id} not found.", Fore.RED)


# Menus
def admin_menu():
    while True:
        colorful_message("\n=== Admin Menu ===", Fore.BLUE)
        print("1. Add Train")
        print("2. View Trains")
        print("3. View Reservations")
        print("4. Cancel Customer Reservation")
        print("5. View Customers")
        print("6. Delete Customer")  # New option
        print("7. Logout")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            add_train()
        elif choice == "2":
            view_trains()
        elif choice == "3":
            reservations = load_reservations()
            if reservations:
                colorful_message("\n=== Reservations ===", Fore.YELLOW)
                for res in reservations:
                    print(Fore.CYAN + f"ID: {res['id']} | Customer: {res['customer_id']} | Train: {res['train_id']} | Seats: {res['seats']}")
            else:
                colorful_message("No reservations found.", Fore.RED)
        elif choice == "4":
            # working

            cancel_reservation()
        elif choice == "5":
            view_customers()
        elif choice == "6":
            delete_customer()
        elif choice == "7":
            colorful_message('Goodbye! Admin, See you soon...', Fore.GREEN)
            break
        else:
            colorful_message("Invalid choice! Try again.", Fore.RED)

def admin_login():
    colorful_message("\n=== Admin Login ===", Fore.YELLOW)
    password = input(Fore.CYAN + "Enter Admin Password: ").strip()
    if password == "admin1234":
        colorful_message("Admin Login Successful!", Fore.GREEN)
        admin_menu()
    else:
        colorful_message("Invalid Password! Access Denied.", Fore.RED)

def customer_menu(customer_id):
    while True:
        colorful_message("\n=== Customer Menu ===", Fore.BLUE)
        print("1. Book Ticket")
        print("2. Cancel Reservation")
        print("3. View Trains")
        print("4. Logout")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            book_ticket(customer_id)
        elif choice == "2":
            cancel_reservation(customer_id)
        elif choice == "3":
            view_trains()
        elif choice == "4":
            colorful_message('Goodbye!', Fore.GREEN)
            break
        else:
            colorful_message("Invalid choice! Try again.", Fore.RED)

def main():
    setup_environment()
    colorful_message("Welcome to Railway Management System", Fore.BLUE)
    while True:
        colorful_message("\n=== Main Menu ===", Fore.YELLOW)
        print("1. Admin Login")
        print("2. Customer Login")
        print("3. Register Customer")
        print("4. Exit")
        choice = input("Enter choice: ").strip()
        if choice == "1":
            admin_login()  # Changed to call the admin login function
        elif choice == "2":
            login_customer()
        elif choice == "3":
            register_customer()
        elif choice == "4":
            colorful_message("Goodbye!", Fore.GREEN)
            break
        else:
            colorful_message("Invalid choice! Please try again.", Fore.RED)

if __name__ == "__main__":
    main()
