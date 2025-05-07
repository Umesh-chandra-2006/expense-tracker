import sqlite3

# Sample data for a year
sample_transactions = [
    (1, 150.00, "Food", "2023-01-01 12:00:00", "expense", "Groceries"),
    (1, 50.00, "Transport", "2023-01-02 09:30:00", "expense", "Gas"),
    (1, 200.00, "Entertainment", "2023-01-03 15:00:00", "expense", "Concert Tickets"),
    (1, 1200.00, "Salary", "2023-01-05 09:00:00", "income", "Monthly Salary"),
    (1, 30.00, "Food", "2023-01-07 19:00:00", "expense", "Dinner Out"),
    (1, 300.00, "Utilities", "2023-01-10 10:00:00", "expense", "Electricity Bill"),
    (1, 80.00, "Transport", "2023-01-12 11:00:00", "expense", "Uber Rides"),
    (1, 600.00, "Entertainment", "2023-01-15 20:00:00", "expense", "Movie Subscription"),
    (1, 500.00, "Food", "2023-01-20 18:00:00", "expense", "Weekly Groceries"),
    (1, 70.00, "Other", "2023-01-21 14:00:00", "expense", "Supplies"),
    (1, -100.00, "Investment", "2023-01-22 14:00:00", "expense", "Stocks"),
    (1, 250.00, "Income", "2023-01-23 14:00:00", "income", "Side Job"),
    (1, -150.00, "Expense", "2023-01-24 14:00:00", "expense", "Unexpected Repair"),
    (1, 600.00, "Salary", "2023-01-30 09:00:00", "income", "Monthly Salary"),
    # Repeat similar pattern for each month with different dates and amounts
    (1, 160.00, "Food", "2023-02-01 12:00:00", "expense", "Groceries"),
    (1, 60.00, "Transport", "2023-02-02 09:30:00", "expense", "Gas"),
    (1, 250.00, "Entertainment", "2023-02-03 15:00:00", "expense", "Concert Tickets"),
    (1, 1300.00, "Salary", "2023-02-05 09:00:00", "income", "Monthly Salary"),
    (1, 40.00, "Food", "2023-02-07 19:00:00", "expense", "Dinner Out"),
    # ... Add more transactions for the remaining months
    (1, 400.00, "Salary", "2023-12-30 09:00:00", "income", "Monthly Salary"),
]

# Connect to the database
conn = sqlite3.connect('expense_tracker.db')
cursor = conn.cursor()

# Insert sample data
cursor.executemany('''INSERT INTO transactions (user_id, amount, category, date, type, description) 
                      VALUES (?, ?, ?, ?, ?, ?)''', sample_transactions)

# Commit and close
conn.commit()
conn.close()
