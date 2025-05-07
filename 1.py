import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

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

# Login Window
def login_window():
    login_win = tk.Tk()
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

# Create the main window
def expense_tracker_gui(user_id):
    window = tk.Tk()
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

    # Transactions Tab Widgets
    add_transaction_ui(transactions_tab, user_id)
    set_budget_ui(budget_tab, user_id)
    view_analytics_ui(analytics_tab, user_id)
    filter_transactions_ui(filter_tab, user_id)

    window.mainloop()

# Add transaction UI
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
        
        # Logic to save the transaction in the database
        cursor.execute('''INSERT INTO transactions (user_id, amount, category, date, type, description) 
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                       (user_id, amount, category, date, type_, description))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Transaction added successfully!")

    tk.Button(tab, text="Add Transaction", command=save_transaction).pack(pady=10)

# Set budget UI
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

# Filter transactions UI
def filter_transactions_ui(tab, user_id):
    tk.Label(tab, text="Filter Transactions", font=("Arial", 14)).pack(pady=10)
    tk.Label(tab, text="(Filter options such as category, date, or amount will be added here)").pack()

# View analytics UI (Budget Analytics)
def view_analytics_ui(tab, user_id):
    tk.Label(tab, text="Budget Analytics", font=("Arial", 14)).pack(pady=10)

    def show_budget_analytics():
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()

        cursor.execute('''SELECT amount FROM budgets WHERE user_id = ?''', (user_id,))
        budget_result = cursor.fetchone()

        if budget_result:
            budget = budget_result[0]

            # Calculate total expenses for the current month
            cursor.execute('''SELECT SUM(amount) FROM transactions WHERE user_id = ? 
                              AND type = 'expense' AND date >= DATE('now', 'start of month')''', (user_id,))
            total_expenses = cursor.fetchone()[0] or 0

            remaining_budget = budget - total_expenses
            used_percentage = (total_expenses / budget) * 100 if budget > 0 else 0

            # Display analytics
            messagebox.showinfo("Budget Analytics", 
                                f"Total Budget: {budget}\n"
                                f"Total Expenses: {total_expenses}\n"
                                f"Remaining Budget: {remaining_budget}\n"
                                f"Budget Used: {used_percentage:.2f}%")
            
            # Generate a pie chart
            labels = ['Used Budget', 'Remaining Budget']
            sizes = [total_expenses, remaining_budget]
            colors = ['#ff9999', '#66b3ff']
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
            plt.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.
            plt.title("Budget Breakdown")
            plt.show()

        else:
            messagebox.showwarning("Warning", "You haven't set a budget yet.")

        conn.close()

    tk.Button(tab, text="View Budget Analytics", command=show_budget_analytics).pack(pady=10)

# Run the database setup
setup_database()
# Start the login window
login_window()
