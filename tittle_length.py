import torch

data = torch.load("./iclr24.da")
papers = data['papers']

primary_area_to_avg_score = {}
title_to_avg_score = {}
id_to_avg_score = {}

count = 0
for paper in papers:
    reviews = paper['reviews']
    scores = []
    if len(reviews) == 0:
        count += 1
        continue
    for review in reviews:
        scores += [int(review['rating'].split(':')[0])]
    title_to_avg_score[paper['title']] = sum(scores) / len(scores)
    id_to_avg_score[int(paper['submission_number'])] = sum(scores) / len(scores)
    if paper['primary_area'] not in primary_area_to_avg_score:
        primary_area_to_avg_score[paper['primary_area']] = []
    primary_area_to_avg_score[paper['primary_area']] += [sum(scores) / len(scores)]
print(count)

# split paper title with length by 5 categories, and compute the average score for each category
categories = {
    '0': range(0, 1),  # Merging 'Very Short' and 'Short'
    '1': range(1, 2),
    '2': range(2, 3),
    '3': range(3, 4),
    '4': range(4, 5),
    '5': range(5, 6),
    '6': range(6, 7),
    '7': range(7, 8),
    '8': range(8, 9),
    '9': range(9, 10),
    '10': range(10, 11),
    '11': range(11, 12),
    '>11': range(12, 10000),
}

# Function to determine category based on title length in words
def get_category(title_length):
    for category, length_range in categories.items():
        if title_length in length_range:
            return category
    return 'Unknown'

# Initialize dictionaries to store total scores and counts for each category
category_scores = {category: 0 for category in categories}
category_counts = {category: 0 for category in categories}

# Categorize each title and aggregate scores
for title, avg_score in title_to_avg_score.items():
    title_length = len(title.split())  # Count words in the title
    category = get_category(title_length)
    category_scores[category] += avg_score
    category_counts[category] += 1

# Calculate average score for each category
category_avg_scores = {category: (category_scores[category] / category_counts[category] if category_counts[category] > 0 else 0) for category in categories}

# Initialize dictionaries to store the sums of squared differences for variance calculation
category_sums_squared_diffs = {category: 0 for category in categories}

# Iterate over titles to accumulate data for variance calculation
for title, avg_score in title_to_avg_score.items():
    title_length = len(title.split())
    category = get_category(title_length)
    # Calculate the squared difference from the mean
    squared_diff = (avg_score - category_avg_scores[category]) ** 2
    category_sums_squared_diffs[category] += squared_diff

# Calculate variance for each category
category_variance = {category: (category_sums_squared_diffs[category] / category_counts[category] if category_counts[category] > 0 else 0) for category in categories}

# Print the results in a formatted way
print("{:<12} {:<15} {:<15} {:<15}".format('Category', 'Avg Score', 'Variance', 'Total Papers'))
for category in categories:
    print("{:<12} {:<15} {:<15} {:<15}".format(category, round(category_avg_scores[category], 2), round(category_variance[category], 2), category_counts[category]))