import torch
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import get_cmap

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
    '<=3': range(0, 4),
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

# Calculate average scores
categories = list(category_scores.keys())
avg_scores = [category_scores[cat] / category_counts[cat] if category_counts[cat] > 0 else 0 for cat in categories]
total_papers = [category_counts[cat] for cat in categories]
all_scores = np.concatenate([[avg_score]*papers for avg_score, papers in zip(avg_scores, total_papers)])  # Flatten scores

# Normalize total_papers for circle sizes in the plot
sizes = np.array(total_papers) / max(total_papers) * 500  # Adjust size scale

# Use a colormap and reverse the color order
cmap = get_cmap('viridis')
colors = cmap(np.linspace(0, 1, len(categories)))[::-1]  # Reversing the color array

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(categories, avg_scores, marker='', linestyle='-', color='deepskyblue')  # Line chart

for i in range(len(categories)):
    plt.scatter(categories[i], avg_scores[i], s=sizes[i], color=colors[i], zorder=5)  # Circle size

# Add a horizontal line for the overall average score
overall_avg_score = np.mean(all_scores)
plt.axhline(y=overall_avg_score, color='red', linestyle='-', linewidth=2)
plt.text(x=0, y=overall_avg_score + 0.01, s=f'Mean Rating: {overall_avg_score:.2f}', color='red', va='bottom')

# Add a horizontal line for the overall median score
overall_median_score = np.median(all_scores)
plt.axhline(y=overall_median_score, color='green', linestyle='-', linewidth=2)
plt.text(x=7, y=overall_median_score + 0.01, s=f'Median Rating: {overall_median_score:.2f}', color='green', va='bottom')

# Aesthetics
plt.xticks(rotation=45)
plt.xlabel('Title Length Category')
plt.ylabel('Paper Avg Rating')
plt.title('Average Score by Title Length Category with Total Papers Represented by Circle Size', pad=25, fontweight='bold')
plt.grid(True)
plt.tight_layout()

# Save plot
plt.savefig('tittle_length.png', dpi=200)