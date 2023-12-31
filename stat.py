import torch
import numpy as np

data = torch.load("./iclr24.da")
papers = data['papers']

total_papers = len(papers)  # Total number of papers
total_reviews = 0  # Total number of reviews
all_scores = []  # List to collect all scores

for paper in papers:
    reviews = paper['reviews']
    if reviews:  # Check if there are reviews
        for review in reviews:
            score = int(review['rating'].split(':')[0])
            all_scores.append(score)
    total_reviews += len(reviews)

# Calculate average and median ratings
average_rating = np.mean(all_scores) if all_scores else 0
median_rating = np.median(all_scores) if all_scores else 0

# Pretty Print the statistics
print(f"Total Number of Papers: {total_papers}")
print(f"Total Number of Reviews: {total_reviews}")
print(f"Average Rating: {average_rating:.2f}")
print(f"Median Rating: {median_rating:.2f}")