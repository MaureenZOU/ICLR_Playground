import time
import os
import re
import argparse
import platform

import torch

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from functools import wraps

def retry(max_attempts):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Attempt {attempts+1}/{max_attempts} failed: {e}")
                    attempts += 1
                    time.sleep(1)  # Optional: wait 1 second between attempts
            print(f"Function {func.__name__} failed after {max_attempts} attempts, returning empty list.")
            return []
        return wrapper
    return decorator

@retry(max_attempts=5)
def fetch_paper_details(driver, url, fetched_ids, paper_id_to_review):
    driver.get(url)
    time.sleep(15)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    paper_list = []
    papers = soup.find_all('div', class_='note undefined') # Update class name as per actual site
    _papers = driver.find_elements(By.CSS_SELECTOR, '.note.undefined')
    for paper, paper_clicker in zip(papers, _papers):
        # Paper Tittle, Keywords, Abstract, Primary Area, pdf_link, Submission Number, Ratings, Confidence
        title_tag = paper.find('a', href=lambda href: href and "/forum?id=" in href)
        paper_title = title_tag.text
        pdf_link = paper.find('a', href=lambda href: href and href.startswith('/attachment?id=') and href.endswith('&name=pdf'))['href']
        primary_area = paper.find('strong', text='Primary Area:', class_='note-content-field').find_next_sibling('span', class_='note-content-value').text
        keywords = paper.find('strong', text='Keywords:', class_='note-content-field').find_next_sibling('span', class_='note-content-value').text
        abstract = paper.find('strong', text='Abstract:', class_='note-content-field').find_next_sibling('div', class_='note-content-value').text
        paper_id = re.search(r"Submission(\d+)", paper_clicker.text).group(1)

        if paper_id in fetched_ids and int(paper_id_to_review[paper_id]) > 0:
            print(f"Paper {paper_id} already fetched. Skipping...")
            continue

        original_tab = driver.current_window_handle
        # click on the paper to get the submission number
        title_link = paper_clicker.find_elements(By.XPATH, ".//a[contains(@href, '/forum?id=')]")[0]
        control_or_command = Keys.COMMAND if platform.system() == 'Darwin' else Keys.CONTROL
        title_link.send_keys(control_or_command + Keys.RETURN)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(15)
        # WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
        _soup = BeautifulSoup(driver.page_source, 'html.parser')
        heading = "Official Review of Submission{}".format(paper_id)
        reviews = _soup.select('div.heading h4 span:contains("{}")'.format(heading))

        review_content = []
        for review in reviews:
            _review = review.find_next('div', class_='note-content-container')
            _rating = _review.find('strong', text='Rating:').find_next('span', class_='note-content-value').text
            _confidence = _review.find('strong', text='Confidence:').find_next('span', class_='note-content-value').text
            review_content += [{"rating": _rating, "confidence": _confidence}]

        paper_list += [{"title": paper_title, "keywords": keywords, "abstract": abstract, "primary_area": primary_area, "pdf_link": pdf_link, "submission_number": paper_id, "reviews": review_content}]
        print("Tittle: {}".format(paper_title), len(review_content), review_content)
        driver.close()
        driver.switch_to.window(original_tab)

    return paper_list

def main():
    parser = argparse.ArgumentParser(description="Script to scrape data from a website")
    parser.add_argument('--webdriver_pth', type=str, required=True, help='Path to the WebDriver executable')
    parser.add_argument('--output_file', type=str, required=True, help='Path to the output file')
    parser.add_argument('--end_page', type=int, default=238, help='Last page number to scrape')
    parser.add_argument('--base_url', type=str, default="https://openreview.net/group?id=ICLR.cc/2024/Conference", help='Base URL of the website')
    parser.add_argument('--start_page', type=int, default=1, help='Start page number')
    parser.add_argument('--check_complete', action='store_true', help='Flag to rerun the problem to double check if all files are crawled')

    args = parser.parse_args()

    service = Service(args.webdriver_pth)
    output_file = args.output_file
    end_page = args.end_page
    base_url = args.base_url
    page_num = args.start_page
    check_complete = args.check_complete

    if os.path.exists(output_file):
        _paper = torch.load(output_file)
    else:
        _paper = {"pages": [], "papers": [], "ids": []}
    
    # paper id to review
    paper_id_to_review = {}
    for paper in _paper["papers"]:
        paper_id_to_review[paper['submission_number']] = len(paper['reviews'])

    options = webdriver.ChromeOptions()
    # options.add_argument("--incognito")
    options.headless = True  # Run in headless mode
    driver = webdriver.Chrome(service=service, options=options)

    driver.get(base_url)
    time.sleep(5)  # Wait for the page to load

    while True:
        print(f"Fetching page {page_num}...")
        
        if page_num in _paper["pages"] and not check_complete:
            print(f"Page {page_num} already fetched. Skipping...")
            page_num += 1
            continue

        # Find the pagination list
        while True:
            pagination_ul = driver.find_element(By.CLASS_NAME, 'pagination')
            page_items = pagination_ul.find_elements(By.XPATH, "//a[@role='button']")
            next_page_item = None

            # Determine the current and next page buttons
            for i, item in enumerate(page_items):
                if item.text == str(page_num):
                    next_page_item = page_items[i]
                    break

            if next_page_item is None:
                if page_items[-3].text == str(end_page):
                    print('Reached the end of the pagination list.')
                    driver.quit()
                    exit()

                next_page_item = page_items[-3]  # Last item in the list
                next_page_item.click()
                time.sleep(15)  # Wait for the new page to load
            else:
                break

        next_page_item.click()
        time.sleep(5)  # Wait for the new page to load
        paper_list = fetch_paper_details(driver, driver.current_url, _paper["ids"], paper_id_to_review)  # Update URL format for pagination
        for paper in paper_list:
            if paper['submission_number'] not in _paper["ids"]:
                _paper["papers"] += [paper]
                _paper["ids"] += [paper['submission_number']]

        if page_num not in _paper["pages"]:
            _paper["pages"] += [page_num]

        torch.save(_paper, output_file)
        page_num += 1

if __name__ == "__main__":
    main()
