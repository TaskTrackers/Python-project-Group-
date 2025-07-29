import mysql.connector
from mysql.connector import Error

# Database configuration
DB_CONFIG = {
    'host': 'localhost',  # Your MySQL host
    'database': 'unilecture_db',
    'user': 'root',       # Your MySQL username
    'password': 'abc123' # !!! IMPORTANT: Replace with your MySQL password
}

def create_connection():
    """Establishes a connection to the MySQL database."""
    connection = None
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("Successfully connected to the database")
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
    return connection

def close_connection(connection):
    """Closes the database connection."""
    if connection and connection.is_connected():
        connection.close()
        print("MySQL connection closed")

if __name__ == '__main__':
    # Example usage:
    conn = create_connection()
    if conn:
        # You can perform some test operations here if needed
        # For example, check server version
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        db_version = cursor.fetchone()
        print(f"Database version: {db_version[0]}")
        cursor.close()
        close_connection(conn)
