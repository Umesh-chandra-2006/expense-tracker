import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

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
    options_menu.add_command(label="Budget Analysis", command=lambda: budget_analysis(user_id))
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
    tree.pack(expand=True, fill='both')

    # Add vertical scrollbar
    scrollbar = ttk.Scrollbar(history_win, orient="vertical", command=tree.yview)
    scrollbar.pack(side='right', fill='y')
    tree.configure(yscroll=scrollbar.set)

    # Add horizontal scrollbar
    h_scrollbar = ttk.Scrollbar(history_win, orient="horizontal", command=tree.xview)
    h_scrollbar.pack(side='bottom', fill='x')
    tree.configure(xscroll=h_scrollbar.set)

    # Load transactions
    load_transactions(user_id)

    # Right-click context menu
    def show_context_menu(event):
        selected_item = tree.selection()
        if selected_item:
            context_menu = tk.Menu(history_win, tearoff=0)
            context_menu.add_command(label="Edit", command=lambda: edit_transaction(selected_item[0], user_id))
            context_menu.add_command(label="Delete", command=lambda: delete_transaction(selected_item[0], user_id))
            context_menu.post(event.x_root, event.y_root)

    tree.bind("<Button-3>", show_context_menu)

# Load transactions
def load_transactions(user_id):
    # Clear existing transactions
    for row in tree.get_children():
        tree.delete(row)

    # Connect to the database and fetch transactions
    conn = sqlite3.connect('expense_tracker.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, amount, category, date, type, description FROM transactions WHERE user_id=?", (user_id,))
    
    # Insert fetched transactions into the tree
    for transaction in cursor.fetchall():
        tree.insert("", tk.END, values=transaction)  # Ensure the values match the order of the columns

    conn.close()

# Budget Analysis with multiple timeframes and chart types
def budget_analysis(user_id):
    analysis_win = tk.Toplevel()
    analysis_win.title("Budget Analysis")
    analysis_win.geometry("400x200")

    tk.Label(analysis_win, text="Select Timeframe:").pack(pady=10)

    timeframe_var = tk.StringVar(value='Monthly')
    tk.Radiobutton(analysis_win, text="Weekly", variable=timeframe_var, value='Weekly').pack(anchor=tk.W)
    tk.Radiobutton(analysis_win, text="Monthly", variable=timeframe_var, value='Monthly').pack(anchor=tk.W)
    tk.Radiobutton(analysis_win, text="Yearly", variable=timeframe_var, value='Yearly').pack(anchor=tk.W)

    def show_analysis():
        timeframe = timeframe_var.get()
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()

        # Determine date range based on timeframe
        if timeframe == 'Weekly':
            cursor.execute("SELECT strftime('%Y-%m-%d', date) AS date, SUM(amount) FROM transactions WHERE user_id=? AND type='expense' AND date >= date('now', '-7 days') GROUP BY date", (user_id,))
        elif timeframe == 'Monthly':
            cursor.execute("SELECT strftime('%Y-%m', date) AS month, SUM(amount) FROM transactions WHERE user_id=? AND type='expense' GROUP BY month", (user_id,))
        else:  # Yearly
            cursor.execute("SELECT strftime('%Y', date) AS year, SUM(amount) FROM transactions WHERE user_id=? AND type='expense' GROUP BY year", (user_id,))

        expenses = cursor.fetchall()
        categories, amounts = zip(*expenses) if expenses else ([], [])

        # Show warning if budget exceeded
        cursor.execute("SELECT amount FROM budgets WHERE user_id=?", (user_id,))
        budget = cursor.fetchone()[0]
        total_expense = sum(amounts)
        if total_expense > budget:
            messagebox.showwarning("Budget Alert", "You have exceeded your budget!")

        # Show charts
        show_charts(categories, amounts, timeframe)
        conn.close()

    tk.Button(analysis_win, text="Show Analysis", command=show_analysis).pack(pady=10)

# Function to display various charts
def show_charts(categories, amounts, timeframe):
    plt.figure(figsize=(15, 5))

    # Pie Chart
    plt.subplot(1, 3, 1)
    wedges, texts, autotexts = plt.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140, pctdistance=0.85)
    plt.setp(autotexts, size=10, weight="bold")
    plt.setp(texts, size=12)
    plt.title(f'Spending Breakdown by Category ({timeframe})')

    # Bar Chart
    plt.subplot(1, 3, 2)
    plt.bar(categories, amounts, color='lightblue')
    plt.title(f'Category Expenses ({timeframe})')
    plt.ylabel('Amount')
    plt.xticks(rotation=45)

    # Generate fluctuating data for line graph
    num_points = 10  # Number of data points for the line graph
    time_labels = np.arange(num_points)  # Time intervals (e.g., days, weeks)
    fluctuations = np.random.normal(loc=0, scale=5, size=num_points)  # Random fluctuations
    expenses = np.cumsum(np.abs(fluctuations))  # Cumulative sum to create a fluctuating line

    # Line Plot for Overall Trend
    plt.subplot(1, 3, 3)
    plt.plot(time_labels, expenses, marker='o', linestyle='-', color='orange')
    plt.title(f'Expenses Over Time ({timeframe})')
    plt.xlabel('Time Interval')
    plt.ylabel('Cumulative Amount')
    plt.xticks(time_labels, [f'Period {i+1}' for i in time_labels])

    plt.tight_layout()
    plt.show()

# Edit transaction
def edit_transaction(item_id, user_id):
    values = tree.item(item_id)['values']
    edit_win = tk.Toplevel()
    edit_win.title("Edit Transaction")
    edit_win.geometry("300x300")

    tk.Label(edit_win, text="Edit Transaction").pack()

    tk.Label(edit_win, text="Amount:").pack()
    amount_entry = tk.Entry(edit_win)
    amount_entry.insert(0, values[1])  # Pre-fill with current value
    amount_entry.pack()

    tk.Label(edit_win, text="Category:").pack()
    category_entry = tk.Entry(edit_win)
    category_entry.insert(0, values[2])  # Pre-fill with current value
    category_entry.pack()

    tk.Label(edit_win, text="Type:").pack()
    type_entry = tk.Entry(edit_win)
    type_entry.insert(0, values[4])  # Pre-fill with current value
    type_entry.pack()

    tk.Label(edit_win, text="Description:").pack()
    description_entry = tk.Entry(edit_win)
    description_entry.insert(0, values[5])  # Pre-fill with current value
    description_entry.pack()

    def update_transaction():
        try:
            amount = float(amount_entry.get())
            category = category_entry.get()
            type_ = type_entry.get()
            description = description_entry.get()
            transaction_id = values[0]  # Get the transaction ID

            # Connect to the database and update the transaction
            conn = sqlite3.connect('expense_tracker.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE transactions SET amount=?, category=?, type=?, description=? WHERE id=?", 
                           (amount, category, type_, description, transaction_id))
            conn.commit()  # Ensure the changes are committed
            conn.close()

            messagebox.showinfo("Success", "Transaction updated successfully!")
            edit_win.destroy()  # Close the edit window
            load_transactions(user_id)  # Refresh transaction history after editing
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount.")

    tk.Button(edit_win, text="Update Transaction", command=update_transaction).pack(pady=10)

# Delete transaction
def delete_transaction(item_id, user_id):
    item_values = tree.item(item_id)['values']
    transaction_id = item_values[0]  # Get the transaction ID
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?"):
        conn = sqlite3.connect('expense_tracker.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE id=?", (transaction_id,))
        conn.commit()  # Ensure the changes are committed
        conn.close()

        messagebox.showinfo("Success", "Transaction deleted successfully!")
        load_transactions(user_id)  # Refresh transaction history after deletion

# Run the application
if __name__ == "__main__":
    setup_database()
    login_window()
