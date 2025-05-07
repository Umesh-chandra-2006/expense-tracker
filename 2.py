import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime
from tkcalendar import DateEntry
from ttkthemes import ThemedTk
import os

# Database setup
def setup_database():
    conn = sqlite3.connect('expense_tracker.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT)''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        amount REAL,
                        category TEXT,
                        date TEXT,
                        type TEXT,
                        description TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
                        user_id INTEGER,
                        amount REAL,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')

    conn.commit()
    conn.close()

# Check if the user is already logged in (persistent login)
def check_persistent_login():
    if os.path.exists("session.txt"):
        with open("session.txt", "r") as file:
            user_id = file.read().strip()
            if user_id:
                return user_id
    return None

# Save user login session
def save_session(user_id):
    with open("session.txt", "w") as file:
        file.write(str(user_id))

# Clear session on logout
def clear_session():
    if os.path.exists("session.txt"):
        os.remove("session.txt")

# Login Window
def login_window():
    login_win = ThemedTk(theme="breeze")  # Using modern theme
    login_win.title("Login")
    login_win.geometry("300x200")

    tk.Label(login_win, text="Username").pack(pady=5)
    username_entry = tk.Entry(login_win)
    username_entry.pack(pady=5)

    tk.Label(login_win, text="Password").pack(pady=5)
    password_entry = tk.Entry(login_win, show="*")
    password_entry.pack(pady=5)

    def login():
        username = username_entry.get()
        password = password_entry.get()
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            messagebox.showinfo("Login Successful", f"Welcome, {username}!")
            save_session(user[0])  # Save session for persistent login
            login_win.destroy()
            expense_tracker_gui(user[0])  # Pass user_id to main GUI
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    tk.Button(login_win, text="Login", command=login).pack(pady=10)
    tk.Button(login_win, text="Signup", command=lambda: signup_window()).pack(pady=5)
    login_win.mainloop()

# Signup Window
def signup_window():
    signup_win = tk.Toplevel()
    signup_win.title("Signup")
    signup_win.geometry("300x250")

    tk.Label(signup_win, text="Username").pack(pady=5)
    username_entry = tk.Entry(signup_win)
    username_entry.pack(pady=5)

    tk.Label(signup_win, text="Password").pack(pady=5)
    password_entry = tk.Entry(signup_win, show="*")
    password_entry.pack(pady=5)

    def signup():
        username = username_entry.get()
        password = password_entry.get()
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            messagebox.showinfo("Signup Successful", "You can now log in.")
            signup_win.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("Signup Failed", "Username already exists.")
        finally:
            conn.close()

    tk.Button(signup_win, text="Create Account", command=signup).pack(pady=10)

# Expense Tracker GUI
def expense_tracker_gui(user_id):
    window = ThemedTk(theme="breeze")  # Using modern theme
    window.title("Enhanced Expense Tracker")
    window.geometry("600x400")

    # Create a tabbed interface
    notebook = ttk.Notebook(window)
    notebook.pack(pady=10, expand=True)

    # Tab 1: Transactions
    transactions_tab = tk.Frame(notebook)
    notebook.add(transactions_tab, text="Transactions")

    # Tab 2: Budget
    budget_tab = tk.Frame(notebook)
    notebook.add(budget_tab, text="Budget")

    # Tab 3: Analytics
    analytics_tab = tk.Frame(notebook)
    notebook.add(analytics_tab, text="Analytics")

    # Tab 4: Filter Transactions
    filter_tab = tk.Frame(notebook)
    notebook.add(filter_tab, text="Filter Transactions")

    # Tab 5: View and Manage Transactions
    manage_tab = tk.Frame(notebook)
    notebook.add(manage_tab, text="Manage Transactions")

    # Transactions Tab Widgets
    add_transaction_ui(transactions_tab, user_id)
    set_budget_ui(budget_tab, user_id)
    view_analytics_ui(analytics_tab, user_id)
    filter_transactions_ui(filter_tab, user_id)
    view_transactions_ui(manage_tab, user_id)

    window.mainloop()

# Add Transaction UI
def add_transaction_ui(tab, user_id):
    tk.Label(tab, text="Add Transaction", font=("Arial", 14)).pack(pady=10)

    tk.Label(tab, text="Amount:").pack()
    amount_entry = tk.Entry(tab)
    amount_entry.pack()

    tk.Label(tab, text="Category:").pack()
    category_var = tk.StringVar()
    category_dropdown = ttk.Combobox(tab, textvariable=category_var)
    category_dropdown['values'] = ("Food", "Transport", "Utilities", "Entertainment", "Other")
    category_dropdown.pack()

    tk.Label(tab, text="Type:").pack()
    type_var = tk.StringVar()
    type_dropdown = ttk.Combobox(tab, textvariable=type_var)
    type_dropdown['values'] = ("income", "expense")
    type_dropdown.pack()

    tk.Label(tab, text="Description:").pack()
    description_entry = tk.Entry(tab)
    description_entry.pack()

    def save_transaction():
        amount = float(amount_entry.get())
        category = category_var.get()
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Current date and time
        type_ = type_var.get()
        description = description_entry.get()

        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO transactions (user_id, amount, category, date, type, description) 
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                       (user_id, amount, category, date, type_, description))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Transaction added successfully!")

    tk.Button(tab, text="Add Transaction", command=save_transaction).pack(pady=10)

# Set Budget UI
def set_budget_ui(tab, user_id):
    tk.Label(tab, text="Set Budget", font=("Arial", 14)).pack(pady=10)

    tk.Label(tab, text="Enter Monthly Budget:").pack()
    budget_entry = tk.Entry(tab)
    budget_entry.pack()

    def save_budget():
        budget = float(budget_entry.get())
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO budgets (user_id, amount) VALUES (?, ?)''', (user_id, budget))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Budget set successfully!")

    tk.Button(tab, text="Set Budget", command=save_budget).pack(pady=10)

# Filter Transactions UI
def filter_transactions_ui(tab, user_id):
    tk.Label(tab, text="Filter Transactions", font=("Arial", 14)).pack(pady=10)

    tk.Label(tab, text="Category:").pack()
    category_var = tk.StringVar()
    category_dropdown = ttk.Combobox(tab, textvariable=category_var)
    category_dropdown['values'] = ("All", "Food", "Transport", "Utilities", "Entertainment", "Other")
    category_dropdown.pack()

    tk.Label(tab, text="Start Date:").pack()
    start_date_entry = DateEntry(tab)
    start_date_entry.pack()

    tk.Label(tab, text="End Date:").pack()
    end_date_entry = DateEntry(tab)
    end_date_entry.pack()

    tk.Label(tab, text="Minimum Amount:").pack()
    min_amount_entry = tk.Entry(tab)
    min_amount_entry.pack()

    tk.Label(tab, text="Maximum Amount:").pack()
    max_amount_entry = tk.Entry(tab)
    max_amount_entry.pack()

    def apply_filters():
        category = category_var.get()
        start_date = start_date_entry.get_date().strftime("%Y-%m-%d")
        end_date = end_date_entry.get_date().strftime("%Y-%m-%d")
        min_amount = min_amount_entry.get() or "0"
        max_amount = max_amount_entry.get() or "99999999"

        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()

        query = '''SELECT * FROM transactions WHERE user_id = ? AND date BETWEEN ? AND ? 
                   AND amount BETWEEN ? AND ?'''
        params = [user_id, start_date, end_date, min_amount, max_amount]

        if category != "All":
            query += " AND category = ?"
            params.append(category)

        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()

        messagebox.showinfo("Filtered Transactions", f"Found {len(results)} transactions.")

    tk.Button(tab, text="Apply Filters", command=apply_filters).pack(pady=10)

# View and Manage Transactions UI
def view_transactions_ui(tab, user_id):
    tk.Label(tab, text="View and Manage Transactions", font=("Arial", 14)).pack(pady=10)

    def refresh_transactions():
        transaction_listbox.delete(0, tk.END)
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM transactions WHERE user_id = ?", (user_id,))
        transactions = cursor.fetchall()
        conn.close()
        
        for trans in transactions:
            transaction_listbox.insert(tk.END, f"ID: {trans[0]}, {trans[3]} - {trans[5]}, ${trans[2]}")

    transaction_listbox = tk.Listbox(tab, height=10, width=50)
    transaction_listbox.pack(pady=10)

    def edit_transaction():
        selected = transaction_listbox.curselection()
        if selected:
            trans_id = transaction_listbox.get(selected).split(",")[0].split(":")[1].strip()
            # Logic for editing

    def delete_transaction():
        selected = transaction_listbox.curselection()
        if selected:
            trans_id = transaction_listbox.get(selected).split(",")[0].split(":")[1].strip()
            conn = sqlite3.connect('expense_tracker.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
            conn.commit()
            conn.close()
            refresh_transactions()
            messagebox.showinfo("Deleted", "Transaction deleted successfully!")

    tk.Button(tab, text="Edit Transaction", command=edit_transaction).pack(pady=5)
    tk.Button(tab, text="Delete Transaction", command=delete_transaction).pack(pady=5)
    
    refresh_transactions()

# Analytics UI (basic analytics can be built here)
def view_analytics_ui(tab, user_id):
    tk.Label(tab, text="Analytics", font=("Arial", 14)).pack(pady=10)
    # Logic for analytics can be added here (charts, statistics, etc.)

# Main function to start the app
def main():
    setup_database()

    user_id = check_persistent_login()
    if user_id:
        expense_tracker_gui(user_id)
    else:
        login_window()

if __name__ == "__main__":
    main()
