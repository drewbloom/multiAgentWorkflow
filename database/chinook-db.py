import sqlite3

# How to establish SQLite db connection
# conn = sqlite3.connect('./database/Chinook_Sqlite.sqlite')
# cursor = conn.cursor()

# Establish a class that can be used for agent to explore the db structure to help with LLM tool use
class SQLQuery:
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        # Connect to the database when the context manager is entered
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close the connection when the context manager is exited
        if self.conn:
            self.conn.close()

    def get_db_structure(self):
        # Get a list of all table names
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in self.cursor.fetchall()]

        # Get the schema for each table
        schemas = {}
        for table in tables:
            self.cursor.execute(f"PRAGMA table_info({table});")
            schemas[table] = self.cursor.fetchall()

        # Get a list of all indexes
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
        indexes = [row[0] for row in self.cursor.fetchall()]

        # Get foreign keys
        foreign_keys = {}
        for table in tables:
            self.cursor.execute(f"PRAGMA foreign_key_list({table});")
            foreign_keys[table] = self.cursor.fetchall()

        return {
            "tables": tables,
            "schemas": schemas,
            "indexes": indexes,
            "foreign_keys": foreign_keys
        }

    def get_triggers(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger';")
        triggers = [row[0] for row in self.cursor.fetchall()]
        return triggers

    def get_views(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='view';")
        views = [row[0] for row in self.cursor.fetchall()]
        return views

    def enable_foreign_keys(self):
        self.cursor.execute("PRAGMA foreign_keys = ON;")


# Example function to handle the entire process (this can be added to an agent class)
def get_database_info(token):
    # Assuming the token is used to get the db_path (for now, directly using it)
    db_path = f"./database/{token}"  # Assuming the token is the filename or part of it
    
    # Using the context manager to handle the connection and automatically close it
    with SQLQuery(db_path) as query:
        # Get the database structure
        database_structure = query.get_db_structure()
        # Can include the following with each run or make them optional - leaving out for now
        # triggers = query.get_triggers()
        # views = query.get_views()

    return {
        "database_structure": database_structure,
        # Leaving other options out for now
        # "triggers": triggers,
        # "views": views
    }

# Example usage
# token = "Chinook_Sqlite.sqlite"  # This would be the user token or database identifier
token = input("Select Database: Type the filename with extension in folder database\n")
result = get_database_info(token)

print(result)

