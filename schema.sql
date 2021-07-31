CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
    username TEXT NOT NULL, 
    hash TEXT NOT NULL, 
    reading_speed TEXT NOT NULL);

CREATE UNIQUE INDEX IF NOT EXISTS username ON users (username);

CREATE TABLE IF NOT EXISTS books (
    user_id INTEGER NOT NULL, 
    book_id INTEGER NOT NULL, 
    title TEXT NOT NULL, 
    cover TEXT NOT NULL, 
    number_of_pages INTEGER NOT NULL, 
    FOREIGN KEY(user_id) REFERENCES users(id));
    