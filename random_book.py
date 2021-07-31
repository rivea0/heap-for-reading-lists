import random

def random_by_page(selected_number, books, pages):
    """Generate random book from the user's list
        for a selected number of pages."""

    # Get books over 500 pages from user's list
    if selected_number == pages[0]:
        found = [i for i in books if i["number_of_pages"] > 500]

    # Get the books with number of pages rounded to the nearest hundred  
    else:
        found = [i for i in books if round(i["number_of_pages"], -2) == int(selected_number)]

    # Get a random result if such books are found
    if found:
        random_result = random.choice(found)
        return random_result


def random_by_time(time_ranges, selected_hour_range, time_stats, books):
    """Generate random book from the user's list with estimated
        reading time within selected hour range"""

    # Get the index of the time ranges list for the selected hour range
    i = time_ranges.index(selected_hour_range)

    # Variable for the intervals between each hour range
    x = 5

    # Get the books with hour range of 0 - 5
    # — the first index has the value "0 - 5" —
    if i == 0:
        found = [k for k, v in time_stats.items() if v in range(x)]
    
    # Get the books with hour range of 20 - 25, including 25 
    # — the last index of time_ranges is 4, with the value "20 - 25" —
    elif i == len(time_ranges) - 1:
        found = [k for k, v in time_stats.items() if v in range(x * i, x * (i + 2))]
    
    # Get the books with the selected hour range, second number included
    else:
        found = [k for k, v in time_stats.items() if v in range(x * i, x * (i + 1))]
    
    random_result = {}

    # Get the random book's title, reading time, and cover
    if found:
        random_result["title"] = random.choice(found)
        random_result["hour"] = time_stats[random_result["title"]]

        for i in books:
            if i["title"] == random_result["title"]:
                random_result["cover"] = i["cover"]

        return random_result