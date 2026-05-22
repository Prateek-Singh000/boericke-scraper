import json
import time
import re
import os
from typing import Optional, Dict, Any, List
import requests
from bs4 import BeautifulSoup, NavigableString, Tag

BASE_URL = "http://homeoint.org/books/boericmm"

def clean_text(text: str) -> str:
    """Strips HTML tags and collapses multiple whitespaces/newlines."""
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def fetch_letter_index(letter: str) -> List[Dict[str, str]]:
    """Crawls a letter index page and extracts remedy links."""
    url = f"{BASE_URL}/{letter}.htm"
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    remedies = []
    
    blockquotes = soup.find_all('blockquote')
    for bq in blockquotes:
        links = bq.find_all('a')
        for a in links:
            abbr = a.get_text(strip=True)
            href = a.get('href')
            if abbr and href and '/' in href:
                full_url = f"{BASE_URL}/{href}" if not href.startswith('http') else href
                remedies.append({
                    "abbreviation": abbr.upper(),
                    "url": full_url
                })
                
    return remedies

def scrape_remedy_page(url: str, letter: str, abbreviation: str) -> Dict[str, Any]:
    """Fetches and parses an individual remedy page into the JSON schema."""
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # 1. Extract Names
    title_element = soup.find('center') or soup.body
    text_content = title_element.get_text(separator='\n').split('\n')
    text_content = [clean_text(t) for t in text_content if clean_text(t)]
    
    full_name = text_content[0] if text_content else abbreviation
    common_name = text_content[1] if len(text_content) > 1 else None

    # 2. Extract Body Content
    general_text = []
    sections = {}
    relationships = None
    current_section = None
    
    for element in soup.body.descendants:
        if isinstance(element, NavigableString):
            text = clean_text(str(element))
            if not text:
                continue
                
            if current_section == "Relationships":
                relationships = (relationships or "") + " " + text
            elif current_section:
                sections[current_section] = sections.get(current_section, "") + " " + text
            else:
                general_text.append(text)
                
        elif isinstance(element, Tag) and element.name == 'b':
            header_text = clean_text(element.get_text())
            header_clean = re.sub(r'[^a-zA-Z0-9\s]', '', header_text).strip()
            
            if "relationship" in header_clean.lower():
                current_section = "Relationships"
            elif header_clean:
                current_section = header_clean
                sections[current_section] = ""

    for k, v in sections.items():
        sections[k] = clean_text(v)
        
    return {
        "abbreviation": abbreviation,
        "full_name": full_name,
        "common_name": common_name,
        "source_url": url,
        "letter": letter.upper(),
        "general": clean_text(" ".join(general_text)),
        "sections": {k: v for k, v in sections.items() if v},
        "relationships": clean_text(relationships) if relationships else None
    }

def main():
    output_file = 'boericke_remedies.json'
    error_file = 'failed_urls.txt'
    
    scraped_data = []
    scraped_urls = set()
    
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            scraped_data = json.load(f)
            scraped_urls = {item['source_url'] for item in scraped_data}
            print(f"Loaded {len(scraped_data)} existing records. Resuming...")

    # TEST MODE: We are only testing the letter 'a' right now
    letters = "abcdefghijklmnopqrstuvwxyz" 
    
    for letter in letters:
        print(f"\n--- Fetching index for letter {letter.upper()} ---")
        try:
            remedies_index = fetch_letter_index(letter)
        except Exception as e:
            print(f"Failed to fetch index for {letter}: {e}")
            continue
            
        for i, item in enumerate(remedies_index):
            url = item['url']
            abbr = item['abbreviation']
            
            if url in scraped_urls:
                continue
                
            print(f"[{letter.upper()}] Scraped {i+1}/{len(remedies_index)} - {abbr}")
            
            try:
                time.sleep(0.75) 
                remedy_data = scrape_remedy_page(url, letter, abbr)
                scraped_data.append(remedy_data)
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(scraped_data, f, indent=2, ensure_ascii=False)
                    
            except Exception as e:
                print(f"  -> Error scraping {url}: {e}")
                with open(error_file, 'a', encoding='utf-8') as ef:
                    ef.write(f"{url}\n")
                continue

if __name__ == "__main__":
    main()