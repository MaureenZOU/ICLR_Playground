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