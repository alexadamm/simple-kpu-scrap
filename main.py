import requests
import logging

REGION_URL = "https://sirekap-obj-data.kpu.go.id/wilayah/pemilu/ppwp"
VOTING_RESULT_URL = "https://sirekap-obj-data.kpu.go.id/pemilu/hhcw/ppwp"

def fetch_json(url):
    """JSON data fetcher from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status() 
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None

def scrape_hierarchy(parent_code="", depth=0):
    """Scrape hierarchical data recursively based on the parent code and depth."""
    if depth == 0:  # Provinces
        url = f"{REGION_URL}/0.json"
    else:
        url = f"{REGION_URL}/{parent_code}.json"
    
    data = fetch_json(url)
    if not data:
        return

    for item in data:
        code = item['kode']
        next_parent_code = f"{parent_code}/{code}" if parent_code else code
        
        if depth < 4:
            scrape_hierarchy(next_parent_code, depth + 1)
        else: 
            scrape_voting_results(next_parent_code, code)

def scrape_voting_results(parent_code, post_code):
    """Scrape voting results for a given post."""
    url = f"{VOTING_RESULT_URL}/{parent_code}.json"
    data = fetch_json(url)
    if not data:
        return
    
    voters01 = voters02 = voters03 = sum_votes = sum_valid_votes = "N/A"
    if data["chart"]:
        voters01 = data["chart"].get("100025", 0)
        voters02 = data["chart"].get("100026", 0)
        voters03 = data["chart"].get("100027", 0)
        sum_votes = voters01 + voters02 + voters03

        if data["administrasi"] and data["administrasi"]["suara_sah"]:
            sum_valid_votes = data["administrasi"]["suara_sah"]
            if sum_votes > sum_valid_votes:
                logging.warning(f"TPS-{post_code}: Sum Votes is greater than Sum Valid Votes; url={url}")
    
    logging.info(f"TPS-{post_code}: Voters 01: {voters01}; 02: {voters02}; 03: {voters03}; Sum Votes: {sum_votes}; Sum Valid Votes: {sum_valid_votes}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    scrape_hierarchy(depth=0)
