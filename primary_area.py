import torch
import numpy as np
import matplotlib.pyplot as plt
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

# Function to calculate variance
def calculate_variance(scores, average):
    variance = sum((x - average) ** 2 for x in scores) / len(scores) if scores else 0
    return variance

# Calculate average, variance, and total count for each primary area
area_stats = {}
for area, scores in primary_area_to_avg_score.items():
    total_papers = len(scores)
    if scores:
        average = sum(scores) / total_papers
        variance = calculate_variance(scores, average)
    else:
        average, variance = 0, 0  # Or handle areas with no scores differently

    area_stats[area] = {'average': average, 'variance': variance, 'total_papers': total_papers}

# Sort primary areas by average score in descending order
sorted_areas = sorted(area_stats.items(), key=lambda x: x[1]['average'], reverse=True)

# Pretty print the results
print("{:<90} {:<15} {:<15} {:<15}".format('Primary Area', 'Average Score', 'Variance', 'Total Papers'))
for area, stats in sorted_areas:
    print("{:<90} {:<15} {:<15} {:<15}".format(area, round(stats['average'], 2), round(stats['variance'], 2), stats['total_papers']))


# Assuming 'sorted_areas' is already computed as in your script
categories = [area[0] for area in sorted_areas]
avg_scores = [stats['average'] for _, stats in sorted_areas]
total_papers = [stats['total_papers'] for _, stats in sorted_areas]
all_scores = [score for area, _ in sorted_areas for score in primary_area_to_avg_score[area]]


# Normalize total_papers for circle sizes in the plot
sizes = np.array(total_papers) / max(total_papers) * 500  # Adjust size scale

# Use a colormap and reverse the color order
cmap = get_cmap('viridis')
colors = cmap(np.linspace(0, 1, len(categories)))[::-1]  # Reversing the color array

# Calculate overall average and median score
overall_avg_score = np.mean(all_scores)
overall_median_score = np.median(all_scores)

# Prepare category labels for x-axis
category_labels = {i + 1: area for i, area in enumerate(categories)}

# Plotting
plt.figure(figsize=(15, 14))
plt.plot(range(1, len(categories) + 1), avg_scores, marker='', linestyle='-', color='deepskyblue')

for i, category in enumerate(categories):
    plt.scatter(i + 1, avg_scores[i], s=sizes[i], color=colors[i], zorder=5)
    # Annotate to the right of the circle
    plt.annotate(category_labels[i + 1], (i + 1, avg_scores[i]), textcoords="offset points", xytext=(12,-2.7), ha='left', fontsize=10, fontweight='bold')

# Add a horizontal line for the overall average and median score
plt.axhline(y=overall_avg_score, color='red', linestyle='-', linewidth=2)
plt.text(x=0, y=overall_avg_score + 0.001, s=f'Mean: {overall_avg_score:.2f}', color='red', va='bottom')

plt.axhline(y=overall_median_score, color='green', linestyle='-', linewidth=2)
plt.text(x=7, y=overall_median_score + 0.001, s=f'Median: {overall_median_score:.2f}', color='green', va='bottom')

# Aesthetics
plt.xticks(ticks=range(1, len(categories) + 1), labels=[f"{i}" for i in range(1, len(categories) + 1)], rotation=45)
plt.xlabel('Primary Area Index')
plt.ylabel('Paper Avg Rating')
plt.title('Average Rating by Primary Area with Total Papers Represented by Circle Size', pad=25, fontweight='bold')
plt.grid(True)
plt.tight_layout()

# Save plot
plt.savefig('primary_area.png', dpi=200)
