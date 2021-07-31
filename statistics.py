import numpy as np

def get_page_stats(books):
    """Group the books in the user's list 
        according to their number of pages."""
    
    page_stats = {}

    for i in books:

        # For number of pages over five hundred
        page_stats["over_five_hund"] = [i for i in books if i["number_of_pages"] > 500]
        
        # For other number of pages (rounded to the nearest hundred)
        page_stats["four_hund"] = [i for i in books if round(i["number_of_pages"], -2) == 400]
        page_stats["three_hund"] = [i for i in books if round(i["number_of_pages"], -2) == 300]
        page_stats["two_hund"] = [i for i in books if round(i["number_of_pages"], -2) == 200]
        page_stats["one_hund"] = [i for i in books if round(i["number_of_pages"], -2) == 100]

        return page_stats


def calc_mins_to_finish(num_pages, reading_speed):
    """Calculate approximate minutes required to finish the book."""

    if reading_speed == 'Slow':
        return num_pages * 2

    elif reading_speed == 'Average':
        return num_pages

    elif reading_speed == 'Fast':
        return num_pages // 2


def calc_mins_to_hours(mins):
    """Convert minutes to rounded hours."""

    hours = mins // 60 

    return hours


def get_time_stats(rows, reading_speed):
    """Get estimated reading time for each book in the list."""

    time_stats = {}
 
    for i in rows:
        mins = calc_mins_to_finish(i["number_of_pages"], reading_speed)
        total_hours = calc_mins_to_hours(mins)
        time_stats[i["title"]] = time_stats.get(total_hours, total_hours)
        
    return time_stats


def get_stats_for_pie_chart(page_stats):
    """Get the books grouped according to their 
        number of pages to create pie chart."""

    # Values list with number of pages in order 
    vals = [
        len(page_stats["over_five_hund"]),
        len(page_stats["four_hund"]),
        len(page_stats["three_hund"]),
        len(page_stats["two_hund"]),
        len(page_stats["one_hund"]),
    ]

    # Return numpy array to create the plot
    return np.array(vals)
