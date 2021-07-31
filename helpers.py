import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session, url_for 
from functools import wraps

from sql_db import create_tables, get_db 


def apology(message, code=400, empty_list=False):
    """Render error message as apology"""
    
    return render_template("apology.html", err=code, msg=message, empty_list=empty_list), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/2.0.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def lookup_title(title):
    """Contact API for the book's title."""

    try:
        url = f"https://openlibrary.org/search.json?title={urllib.parse.quote_plus(title)}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None


def lookup_editions(response):
    """Contact API for the editions of the book."""

    if response:
        try:
            k = response["docs"][0]["key"]
            edition_search = f"https://openlibrary.org{k}/editions.json?limit=10"
            editions = requests.get(edition_search)
            editions.raise_for_status()
            return editions.json()
        except (requests.RequestException, KeyError, ValueError, IndexError):
            return None
    

def get_cover(item):
    """Get the cover image of an edition."""

    c = item["covers"][0]
    cover_url = f"http://covers.openlibrary.org/b/id/{c}-M.jpg"
    
    return cover_url


def get_author(item):
    """Get the author's name of the book."""

    a_key = item["authors"][0]["key"]
    author_url = f"http://openlibrary.org{a_key}.json"
    try:
        author_result = requests.get(author_url).json()
        return author_result["name"]
    except (requests.RequestException, KeyError, ValueError, IndexError):
        return None


def lookup(title):
    """Look up information about the book and
        load the editions into a dictionary."""
    try:
        response = lookup_title(title)
        editions = lookup_editions(response)
    except requests.RequestException:
        return None

    if editions:
        try:
            # Create editions dictionary
            eds = {}

            # Initialize count to track editions  
            count = 0

            for i in editions["entries"]:
                # Get the edition only if it has "number of pages",
                # otherwise you cannot calculate the required stats for the app
                if "number_of_pages" in i:

                    # Create dictionary for the edition
                    eds[count] = {}

                    if "authors" in i:
                        eds[count]["author"] = get_author(i)

                    if "covers" in i:
                        eds[count]["cover"] = get_cover(i)
                    else:
                        non_cover = "cover_not_found.jpg"
                        eds[count]["cover"] = os.path.join("static/images/", non_cover)
                
                    if "publish_date" in i:
                        eds[count]["publish_date"] = i["publish_date"]

                    eds[count]["id"] = count
                    eds[count]["title"] = i["title"]
                    eds[count]["number_of_pages"] = i["number_of_pages"]
            
                    count += 1

            return eds

        except (KeyError, ValueError, IndexError):
            return None