import sqlite3
def create_tables():
# Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect('nextstep.db')

# Create a cursor object to execute SQL queries
    cur = conn.cursor()

# Define the SQL query to create the table with a TEXT column
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS rapport (
        id INTEGER PRIMARY KEY,
        filename TEXT NOT NULL,
        content TEXT NOT NULL
    )
    '''

# Execute the SQL query to create the table
    cur.execute(create_table_query)

# Commit the transaction (save changes)
    conn.commit()

# Close the cursor and connection
    cur.close()
    conn.close()
