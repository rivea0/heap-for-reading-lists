import matplotlib
matplotlib.use("Agg")
import sqlite3

from flask import Flask, flash, redirect, render_template, request, session, url_for 
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from charts import create_histogram, create_pie_chart
from helpers import apology, login_required, lookup
from random_book import random_by_page, random_by_time
from sql_db import create_tables, get_db
from statistics import get_page_stats, get_stats_for_pie_chart, get_time_stats

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Create tables for the SQLite3 database
create_tables()

@app.route("/")
def index():
    """Display the site's purpose."""
    
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 403)
        
        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("Must provide password", 403)

        # Get the username and password fields
        username = request.form.get("username")
        password = request.form.get("password")

        # Connect to database
        db = get_db()

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Close the database
        db.close()

        # Redirect user to their overview page
        return redirect("/overview")

    # If the method is GET
    else:
        return render_template("login.html")


@app.route("/about")
def about():
    """Display about page."""

    return render_template("about.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""

    # Approximate reading speed values
    speed_values = ["Slow", "Average", "Fast"]

    # Get the username, password, confirmation, and reading speed
    username = request.form.get("username")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    speed = request.form.get("speed")

    if request.method == "POST":
        
        # Check if any required field is missing
        if (not username or not password or not confirmation or 
            speed not in speed_values):
            return apology("Missing input field", 400)

        # Connect to database
        db = get_db()

        # Check if username already exists
        usernames = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()
        if len(usernames) != 0:
            return apology("Username already exists", 400)

        # Check if the password fields match
        if password != confirmation:
            return apology("Passwords do not match", 400)

        # Register the user
        db.execute("INSERT INTO users (username, hash, reading_speed) VALUES (:username, :hash, :speed)", 
                   {"username": username,
                   "hash": generate_password_hash(password, method='pbkdf2:sha256', salt_length=16), 
                   "speed": speed})

        db.commit()

        # Remember the user
        rows = db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchall()
        session["user_id"] = rows[0]["id"]

        db.close()

        # Display message
        flash("Registered!")

        # Return user to homepage
        return redirect("/")

    # If the method is GET
    else:
        return render_template("register.html", speed_values=speed_values)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search editions for a given title."""

    if request.method == "POST":

        # Get the title field
        title = request.form.get("title")
        
        # Look up editions
        editions_result = lookup(title)
        
        # Check if editions exist
        if editions_result == None or len(editions_result) == 0:
            return apology("Could not find results", 400)

        # Return add page with found editions
        return render_template("add.html", title=title, editions_result=editions_result)

    # If the method is GET, display search page  
    else:
        return render_template("search.html")


@app.route("/add/<title>", methods=["GET", "POST"])
@login_required
def add(title):
    """Add chosen edition into list."""

    # If the user adds book to their list
    if request.method == "POST":
        # Get the chosen edition's id
        chosen_edition_id = request.form.get("edition")

        if not chosen_edition_id:
            return apology("You must choose an edition", 400)

        # Load the edition results of title
        results = lookup(title)

        # Check if editions exist
        if results == None or len(results) == 0:
            return apology("Could not find results", 400)

        # Get the selected edition from editions
        try:
            result = results[int(chosen_edition_id)]
        except KeyError:
            return apology("Could not find results", 400)

        title = result["title"]
        cover = result["cover"]
        number_of_pages = result["number_of_pages"]
        book_id = result["id"]

        # Connect to database and get user's books
        db = get_db()
        books = db.execute("SELECT * FROM books WHERE user_id = :user_id", {"user_id": session["user_id"]}).fetchall()

        book_list = [i["title"] for i in books]

        # Check if the user selected a book that's already on their list
        if result["title"] in book_list:
            return apology("Book already in list", 400)

        # Add book (the edition) to user's list
        db.execute("""INSERT INTO books
            (title, cover, number_of_pages, book_id, user_id) VALUES (:title, :cover, :number, :book_id, :user_id)""", 
            {"title": title, "cover": cover, "number": number_of_pages, "book_id": book_id, "user_id": session["user_id"]})

        db.commit()
        db.close()

        # Display message
        flash("Added book!")

        return redirect("/overview")

    # If the method is GET, display editions of searched title
    else:
        return render_template("add.html", title=title)


@app.route("/get-random-by-page", methods=["GET", "POST"])
@login_required
def get_random_by_page():
    """Get a random book from the list for a selected number of pages."""
    
    # Approximate number of pages
    pages = ["Over 500", "400", "300", "200", "100"]

    if request.method == "POST":

        # Get the chosen number of pages
        chosen_num_pages = request.form.get("page")

        if chosen_num_pages not in pages:
            return apology("Invalid field", 400)

        # Get user's books
        db = get_db()
        books = db.execute("SELECT * FROM books WHERE user_id = :user_id", {"user_id": session["user_id"]}).fetchall()

        # Generate random book 
        result = random_by_page(chosen_num_pages, books, pages)

        db.close()

        # Check if the result is valid (if the user's list has such book)
        if result:
            return render_template("get-random-by-page.html", result=result)
        else:
            return apology("No books with selected number of pages", 400)

    else:
        # Display pages list for user to choose
        return render_template("get-random-by-page.html", pages=pages)


@app.route("/get-random-by-time", methods=["GET", "POST"])
def get_random_by_time():
    """Get a random book from the list for a selected reading time range."""

    # Approximate time ranges (hours)
    time_ranges = ["0 - 5", "5 - 10", "10 - 15", "15 - 20", "20 - 25"]

    # Connect to database, get user's list and reading speed
    db = get_db()
    rows = db.execute("SELECT * FROM books WHERE user_id = :user_id", {"user_id": session["user_id"]}).fetchall()
    speed = db.execute("SELECT reading_speed FROM users WHERE id = :user_id", {"user_id": session["user_id"]}).fetchone()
    db.close()

    # Get reading time of all the books
    book_hrs = get_time_stats(rows, speed[0])

    # Get the selected reading time range
    selected_hour = request.form.get("hour")

    if request.method == "POST":

        # Generate random book for a given reading time
        result = random_by_time(time_ranges, selected_hour, book_hrs, rows)        

        # Check if the result is valid (if the user's list has such book)
        if result:
            return render_template("get-random-by-time.html", result=result)
        else:
            return apology("No books with selected time range", 400)

    else:
        return render_template("get-random-by-time.html", time_ranges=time_ranges)


@app.route("/logout")
def logout():
    """Log user out."""

    # Forget any user_id
    session.clear()
    
    return redirect("/")


@app.route("/overview")
@login_required
def overview():
    """Present an overview of the user's reading list."""
    
    # Get the user's books
    db = get_db()    
    rows = db.execute("SELECT * FROM books WHERE user_id = :user_id", {"user_id": session["user_id"]}).fetchall()

    # Check if the user has an empty list
    if len(rows) == 0:
        return apology("You have not added any books yet!", 400, empty_list=True)

    # Group the books according to their number of pages
    grouped_pages = get_page_stats(rows)

    # Create a pie chart displaying the percentages of books according to their number of pages
    pie_values = get_stats_for_pie_chart(grouped_pages)
    pie_filepath = create_pie_chart(pie_values)

    # Get the user's approximate reading speed
    speed = db.execute("SELECT reading_speed FROM users WHERE id = :user_id", {"user_id": session["user_id"]}).fetchone()
    
    db.close()

    # Get the estimated reading time of books in the list,
    # create a histogram displaying the time ranges in hours and
    # the number of books that fall within each range
    hrs = get_time_stats(rows, speed[0])
    histogram_filepath = create_histogram(hrs)

    return render_template("overview.html", grouped_pages=grouped_pages, 
                           pie_filepath=pie_filepath, histogram_filepath=histogram_filepath)


@app.route("/remove", methods=["POST"])
@login_required
def remove():
    """Remove books from the user's list."""

    # Get the book to be removed
    book_title = request.form.get("book_title")

    # Connect to database and delete the book from user's list
    db = get_db()
    db.execute("DELETE FROM books WHERE user_id = :user_id AND title = :book_title", 
               {"user_id": session["user_id"], "book_title": book_title})
    db.commit()

    db.close()

    return redirect("/overview")


@app.route("/pwd-confirm", methods=["GET", "POST"])
@login_required
def pwd_confirm():
    """Request user to confirm their password 
        in order to delete their account."""

    if request.method == "POST":
    
        pwd = request.form.get("password")

        # Get the user from database
        db = get_db()
        rows = db.execute("SELECT * FROM users WHERE id = :user_id", {"user_id": session["user_id"]}).fetchall()

        # Check if password fields match
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], pwd):
            return apology("Fields do not match", 400)
        else:
            # Delete the user from database
            db.execute("DELETE FROM users WHERE id = :user_id", {"user_id": session["user_id"]})
            db.commit()
            db.close()

            session.clear()

            # Display message
            flash("Account deleted!")

            return redirect("/")
    else:
        return render_template("pwd-confirm.html")
