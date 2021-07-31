import math
import matplotlib.pyplot as plt
import numpy as np
import os

def create_pie_chart(values):
    """Generate pie chart for the number of pages 
        of the books in user's list."""
    
    # Organize labels according to approximate number of pages
    page_labels = ["Over 500 pages", "~400 pages", "~300 pages", "~200 pages", "~100 pages"]
    
    # Generate colors for the pie chart
    pie_colors = ["#FF0055", "#46F973", "#ED7DED", "#00FFFF", "#FF8000"]

    # Create the chart with percentage values
    plt.pie(values, colors=pie_colors, shadow=True, autopct="%1.1f%%")
    
    # Create legend for the chart
    plt.legend(labels=page_labels, loc='upper right', bbox_to_anchor=(0.77, 0.55, 0.5, 0.5), fontsize=10, labelspacing=1)
    
    # Save the chart image
    filename = "overview_pie.png"
    f_path = os.path.join("static/images/", filename)
    plt.savefig(f_path, bbox_inches='tight', pad_inches=0)
    plt.close()

    return f_path


def create_histogram(time_stats):
    """Generate a histogram for the estimated reading time
        of the books in user's list."""

    # Get the books' reading time stats
    books_hours = [time_stats[k] for k in time_stats.keys()]

    # Create figure and subplots
    fig, ax = plt.subplots(1, 1)

    hours = np.array(books_hours)

    # Create histogram with bins according to approximate time ranges
    ax.hist(hours, bins = [0, 5, 10, 15, 20, 25], color='#7F00FF', edgecolor="#00ffff")

    ax.set_xticks([0, 5, 10, 15, 20, 25])

    ax.set_xlabel('Ranges of Hours')
    ax.set_ylabel('Number of Books')

    # Save the chart image
    filename = "overview_histogram.png"
    f_path = os.path.join("static/images/", filename)
    plt.savefig(f_path, bbox_inches='tight', pad_inches=0.3)
    plt.close()

    return f_path
