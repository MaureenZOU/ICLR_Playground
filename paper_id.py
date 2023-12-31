import torch
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap

# Load data
data = torch.load("./iclr24.da")
papers = data['papers']

# Initialize the data structure for intervals
intervals = [(0, 100), (100, 1000), (1000, 2000), (2000, 3000), (3000, 4000),
             (4000, 5000), (5000, 6000), (6000, 7000), (7000, 8000), (8000, 9000), (9000, 10000)]
stats = {interval: {'total_scores': [], 'total_papers': 0} for interval in intervals}

# Process each paper
for paper in papers:
    paper_id = int(paper['submission_number'])
    reviews = paper['reviews']

    if len(reviews) > 0:
        scores = [int(review['rating'].split(':')[0]) for review in reviews]
        avg_score = sum(scores) / len(scores)

        # Assign paper to the correct interval
        for interval in intervals:
            if interval[0] <= paper_id < interval[1]:
                stats[interval]['total_scores'].append(avg_score)
                stats[interval]['total_papers'] += 1
                break

# Prepare data for plotting
categories, avg_scores, total_papers = [], [], []
for interval, data in stats.items():
    categories.append(f"{interval[0]}-{interval[1]}")
    if data['total_papers'] > 0:
        avg_scores.append(np.mean(data['total_scores']))
    else:
        avg_scores.append(0)
    total_papers.append(data['total_papers'])

all_scores = []
for data in stats.values():
    all_scores.extend(data['total_scores'])
overall_avg_score = np.mean(all_scores) if all_scores else 0

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
plt.axhline(y=overall_avg_score, color='red', linestyle='-', linewidth=2)
# Add text annotation for the overall average score
plt.text(x=0, y=overall_avg_score + 0.01, s=f'Mean Rating: {overall_avg_score:.2f}', color='red', va='bottom')

# Add a horizontal line for the overall median score
overall_median_score = np.median(all_scores) if all_scores else 0
plt.axhline(y=overall_median_score, color='green', linestyle='-', linewidth=2)
plt.text(x=7, y=overall_median_score + 0.01, s=f'Median Rating: {overall_median_score:.2f}', color='green', va='bottom')

# Aesthetics
plt.xticks(rotation=45)
plt.xlabel('Paper ID Range')
plt.ylabel('Paper Avg Rating')
plt.title('Average Rating by Paper ID Range with Total Valid Papers Represented by Circle Size', pad=25, fontweight='bold')
plt.grid(True)
plt.tight_layout()

# Save plot
plt.savefig('paper_id.png', dpi=200)

# Pretty Print the results
print("{:<15} {:<15} {:<15} {:<15}".format('Category', 'Avg Score', 'Variance', 'Total Papers'))
for interval, data in stats.items():
    if data['total_papers'] > 0:
        avg_score = np.mean(data['total_scores'])
        variance = np.var(data['total_scores'])
    else:
        avg_score = 0
        variance = 0

    print("{:<15} {:<15} {:<15} {:<15}".format(f"{interval[0]}-{interval[1]}", 
                                               f"{avg_score:.2f}", 
                                               f"{variance:.2f}", 
                                               data['total_papers']))