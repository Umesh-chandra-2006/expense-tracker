import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

# Database setup
def setup_database():
    conn = sqlite3.connect('expense_tracker.db')
    cursor = conn.cursor()

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
            check_if_budget_exists(user[0])  # Pass user_id to check budget
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

# Check if budget exists
def check_if_budget_exists(user_id):
    conn = sqlite3.connect('expense_tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT amount FROM budgets WHERE user_id=?", (user_id,))
    budget = cursor.fetchone()
    conn.close()

    if budget:
        expense_tracker_gui(user_id)  # If budget exists, proceed to main app
    else:
        set_budget_first(user_id)  # Prompt to set budget

# Set budget first if new user
def set_budget_first(user_id):
    set_budget_win = tk.Tk()
    set_budget_win.title("Set Budget")
    set_budget_win.geometry("300x200")

    tk.Label(set_budget_win, text="Enter Your Monthly Budget:").pack(pady=10)
    budget_entry = tk.Entry(set_budget_win)
    budget_entry.pack(pady=10)

    def save_initial_budget():
        budget = float(budget_entry.get())
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO budgets (user_id, amount) VALUES (?, ?)", (user_id, budget))
        conn.commit()
        conn.close()
        messagebox.showinfo("Budget Set", "Your budget has been set.")
        set_budget_win.destroy()
        expense_tracker_gui(user_id)  # Proceed to main app

    tk.Button(set_budget_win, text="Save Budget", command=save_initial_budget).pack(pady=10)
    set_budget_win.mainloop()

# Main window with side navigation
def expense_tracker_gui(user_id):
    global tree, history_win
    window = tk.Tk()
    window.title("Expense Tracker")
    window.geometry("600x400")

    # Top menu with a three-bar icon
    menubar = tk.Menu(window)
    window.config(menu=menubar)

    options_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="☰", menu=options_menu)
    options_menu.add_command(label="Edit Budget", command=lambda: edit_budget(user_id))
    options_menu.add_command(label="Transaction History", command=lambda: view_transaction_history(user_id))
    options_menu.add_command(label="Custom Trend Analysis", command=lambda: custom_trend_analysis(user_id))
    options_menu.add_command(label="Logout", command=window.quit)

    # Create a tabbed interface
    notebook = ttk.Notebook(window)
    notebook.pack(pady=10, expand=True)

    # Tab 1: Transactions
    transactions_tab = tk.Frame(notebook)
    notebook.add(transactions_tab, text="Transactions")

    # Transactions Tab Widgets
    add_transaction_ui(transactions_tab, user_id)

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
        try:
            amount = float(amount_entry.get())
            category = category_var.get()
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            amount_entry.delete(0, tk.END)  # Clear input fields
            category_var.set('')
            type_var.set('')
            description_entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    tk.Button(tab, text="Add Transaction", command=save_transaction).pack(pady=10)

# Edit budget
def edit_budget(user_id):
    edit_win = tk.Toplevel()
    edit_win.title("Edit Budget")
    edit_win.geometry("300x200")

    tk.Label(edit_win, text="Enter New Monthly Budget:").pack(pady=10)
    budget_entry = tk.Entry(edit_win)
    budget_entry.pack(pady=10)

    def update_budget():
        budget = float(budget_entry.get())
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE budgets SET amount = ? WHERE user_id = ?", (budget, user_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Budget updated successfully!")
        edit_win.destroy()

    tk.Button(edit_win, text="Update Budget", command=update_budget).pack(pady=10)

# View transaction history with sorting/filtering options
def view_transaction_history(user_id):
    global history_win, tree
    if 'history_win' in globals() and history_win.winfo_exists():
        history_win.lift()  # Bring the existing window to the front
        return

    history_win = tk.Toplevel()
    history_win.title("Transaction History")
    history_win.geometry("600x400")

    tree = ttk.Treeview(history_win, columns=("S.No", "Amount", "Category", "Date", "Type", "Description"), show="headings")
    tree.heading("S.No", text="S.No")
    tree.heading("Amount", text="Amount")
    tree.heading("Category", text="Category")
    tree.heading("Date", text="Date")
    tree.heading("Type", text="Type")
    tree.heading("Description", text="Description")
    tree.pack(expand=True, fill="both")

    # Fetch transaction history
    conn = sqlite3.connect('expense_tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, amount, category, date, type, description FROM transactions WHERE user_id=?", (user_id,))
    transactions = cursor.fetchall()
    conn.close()

    for transaction in transactions:
        tree.insert("", "end", values=transaction)

    # Add scrollbar
    scrollbar = ttk.Scrollbar(history_win, orient="vertical", command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side='right', fill='y')

# Custom trend analysis
def custom_trend_analysis(user_id):
    analysis_win = tk.Toplevel()
    analysis_win.title("Custom Trend Analysis")
    analysis_win.geometry("400x300")

    tk.Label(analysis_win, text="Select Date Range:").pack(pady=10)

    tk.Label(analysis_win, text="Start Date (YYYY-MM-DD):").pack()
    start_date_entry = tk.Entry(analysis_win)
    start_date_entry.pack(pady=5)

    tk.Label(analysis_win, text="End Date (YYYY-MM-DD):").pack()
    end_date_entry = tk.Entry(analysis_win)
    end_date_entry.pack(pady=5)

    def show_trends():
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()

        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        
        # Query to get total expenses by date
        cursor.execute('''
            SELECT strftime('%Y-%m-%d', date) AS date, SUM(amount) 
            FROM transactions 
            WHERE user_id=? AND date BETWEEN ? AND ? AND type='expense' 
            GROUP BY date 
            ORDER BY date
        ''', (user_id, start_date, end_date))
        
        results = cursor.fetchall()
        conn.close()

        # Prepare data for plotting
        dates, amounts = zip(*results) if results else ([], [])
        
        if amounts:
            # Plotting the trends
            plt.figure(figsize=(10, 5))
            plt.plot(dates, amounts, marker='o')
            plt.title("Custom Expense Trends")
            plt.xlabel("Date")
            plt.ylabel("Total Expenses")
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.grid()
            plt.show()
        else:
            messagebox.showinfo("No Data", "No expenses found for the selected date range.")

    tk.Button(analysis_win, text="Show Trends", command=show_trends).pack(pady=10)

# Run the application
if __name__ == "__main__":
    setup_database()
    login_window()
