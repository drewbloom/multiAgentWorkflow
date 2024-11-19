import sqlite3

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

        self.enable_foreign_keys()

        return {
            "tables": tables,
            "schemas": schemas,
            "indexes": indexes,
            "foreign_keys": foreign_keys
        }
    
    def llm_query(self, llm_input):
        result = self.cursor.execute(llm_input)
        return result

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