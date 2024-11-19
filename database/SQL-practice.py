import sqlite3

class QueryTest:
    def __init__(self, path):
        self.path = path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        # only initiate connections when context manager enters
        self.conn = sqlite3.connect(self.path)
        self.cursor = self.conn.cursor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # close connection when context manager is exited
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
    
    def llm_query(self, llm_input):
        result = self.cursor.execute(llm_input)
        return result

    
    def unsecured_fstring_artist_by_track(self):
        track_name = input("Enter the track title:\n")
        
        self.cursor.execute(f"""
                            SELECT Artist.Name
                            FROM Track
                            JOIN Album ON Track.AlbumID = Album.AlbumID
                            JOIN Artist ON Album.ArtistId = Artist.ArtistId
                            WHERE Track.Name = '{track_name}';""")
        artist_match = self.cursor.fetchall() # can perform fetchone() if you want to only return 1st result
        if artist_match:
            return artist_match
        else:
            return f"No artist found for track '{track_name}'"

    def search_artist_by_track(self):
        track_name = input("Enter the track title:\n")
        
        self.cursor.execute("""
                            SELECT Artist.Name
                            FROM Track
                            JOIN Album ON Track.AlbumID = Album.AlbumID
                            JOIN Artist ON Album.ArtistId = Artist.ArtistId
                            WHERE Track.Name = ?;""", (track_name,)) # Keep comma after track_name - otherwise, it reads the string as characters - should be a single-item tuple to read properly
        artist_match = self.cursor.fetchone() # can perform fetchone() if you want to only return 1st result
        if artist_match:
            return artist_match
        else:
            return f"No artist found for track '{track_name}'"
    
    def get_all_tracks_for_artist(self):
        artist_name = input("What artist would you like to get tracks for?\n")

        query = f"""SELECT Track.Name
                            FROM Track
                            JOIN Album ON Track.AlbumId = Album.AlbumId
                            JOIN Artist ON Album.ArtistId = Artist.ArtistId 
                            WHERE Artist.Name = ?"""
        
        self.cursor.execute(query, (artist_name,))

        track_matches = self.cursor.fetchall()

        if track_matches:
            return track_matches
        else:
            return f"No tracks found matching artist '{artist_name}'"
        
    def get_albums_for_artist(self):
        artist_name = input("What artist would you like to get albums for?\n")

        query = f"""SELECT Album.Title
                    FROM Album
                    JOIN Artist ON Album.ArtistId = Artist.ArtistId
                    WHERE Artist.Name = ?"""
        
        self.cursor.execute(query, (artist_name,))

        albums = self.cursor.fetchall()

        if albums:
            return albums
        else:
            return f"No albums found for artist '{artist_name}'"

# Main method to allow user to try different database files and queries from the console
def main():
    directory = "../database/"
    filename = "Chinook_Sqlite.sqlite" # input("Database file: Enter the filename with its extension\n")
    path = f'{directory}{filename}'
    print(f"Using database file: {path}")

    try:
        with QueryTest(path) as query:
            while True:
                # List the methods programmatically (filter out non-callable and internal methods)
                methods = [method for method in dir(query) if callable(getattr(query, method)) and not method.startswith("__")]
                
                # Create a numbered menu for the user
                print("\nSelect a method to run:")
                for i, method in enumerate(methods, 1):
                    print(f"{i}. {method}")

                # Prompt user for selection
                user_input = input("\nEnter the number of the method to run (or 'q' to quit): ").strip()

                if user_input.lower() == 'q':
                    print("Exiting...")
                    break

                # Validate input and call the selected method
                if user_input.isdigit():
                    method_number = int(user_input)
                    if 1 <= method_number <= len(methods):
                        method_name = methods[method_number - 1]
                        method_to_call = getattr(query, method_name)
                        result = method_to_call()
                        print(f"Result of '{method_name}': {result}\n")
                    else:
                        print("Invalid method number. Please select a valid method.\n")
                else:
                    print("Invalid input. Please enter a number or 'q' to quit.\n")

    except Exception as e:
        print(f"Error: {e}")

# Run the program
if __name__ == "__main__":
    main()