#Python import used for consistency
import re
#Python Imports for basic web-scraping
import requests
from bs4 import BeautifulSoup

def extract_website_from_md(md_text):  # Takes URL from .md file
    patterns = [
        r"https?://[^\s\)]+",
        r"www\.[^\s\)]+"
    ]
    for pattern in patterns:
        match = re.search(pattern, md_text, re.IGNORECASE)
        if match:
            url = match.group(0).strip()
            # Remove URL fragments and query params
            url = url.split('#')[0].split('?')[0]
            if not url.startswith("http"):
                url = "https://" + url
            return url
    return None

def scrape_public_data(URL):  # Function scrapes the extracted URL and multiple pages
    base_url = URL.rstrip('/')  # Remove trailing slash if present
    
    # Headers to mimic a real browser (avoids basic bot blocking)
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }
    
    # Common website paths to attempt scraping
    pages = [
        "",
        "/about",
        "/about-us",
        "/products",
        "/services"
    ]
    
    # Store results for each page separately
    scraped_pages = []
    all_text = ""
    
    for page in pages:
        full_url = base_url + page
        try:
            response = requests.get(full_url, headers=headers, timeout=10)
            response.raise_for_status()  # Verify response was successful
            
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            
            page_text = []
            for p in paragraphs:
                text = p.get_text(strip=True)
                if len(text) > 50:  # Filter out short paragraphs
                    page_text.append(text)
            
            # Only add if we actually got content
            if page_text:
                combined_text = " ".join(page_text)
                scraped_pages.append({
                    "url": full_url,
                    "text": combined_text
                })
                all_text += combined_text + " "
                #print(f"Successfully scraped: {full_url} ({len(page_text)} paragraphs)")
                
        except requests.RequestException as e:
            #print(f" Failed to scrape {full_url}: {str(e)}")
            continue
    
    # Limit total text length to avoid memory issues
    if len(all_text) > 100000:
        all_text = all_text[:100000]
    
    # Return both combined and individual results
    return {
        "raw_text": all_text.strip(),
        "source_urls": [page["url"] for page in scraped_pages],
        "pages": scraped_pages,  # Individual page data
        "total_pages_scraped": len(scraped_pages)
    }
