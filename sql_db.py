import sqlite3

def get_db():
    """Connect to the database"""

    db = sqlite3.connect("heap.db")
    
    # Configure database to access columns by name.  
    # https://docs.python.org/3.9/library/sqlite3.html#sqlite3.Row 
    db.row_factory = sqlite3.Row

    return db 


def create_tables():
    """Create tables for the database"""

    db = get_db()

    with open("schema.sql") as f:
        db.executescript(f.read())

    db.commit()
    db.close()
    