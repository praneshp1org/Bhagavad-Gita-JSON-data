import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import os
import time
from tqdm import tqdm

def scrape_page_content(url):
    """
    Scrapes main text content from a given page URL.
    """
    try:
        print(f"  -> Scraping content from: {url}")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        page = {"heading": soup.select_one("h1").text.strip() if soup.select_one("h1") else "No Heading"}
        page['body'] = []

        # Extract text from main content blocks
        selectors = [".text-center", ".text-base", ".em\\:mb-4.em\\:leading-8.em\\:text-base.s-justify"]
        for selector in selectors:
            for elem in soup.select(selector):
                text = elem.get_text(strip=True)
                if text:
                    page['body'].append(text)

        content_text = "\n".join(page['body'])
        return content_text

    except requests.exceptions.RequestException as e:
        print(f"    [Error] Could not fetch {url}: {e}")
        return None
    except Exception as e:
        print(f"    [Error] An error occurred while scraping {url}: {e}")
        return None

def scrape_vedabase_bg_chapters():
    """
    Scrapes introductory and chapter links from Bhagavad-gītā on vedabase.io,
    then scrapes sub-links from each and saves everything to JSON.
    """
    base_url = "https://vedabase.io"
    library_url = f"{base_url}/en/library/bg/"
    
    # --- Output Directory ---
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(script_dir, "json_output")
    os.makedirs(output_dir, exist_ok=True)
    output_filename = os.path.join(output_dir, "gita.json")
    
    print(f"Scraping index page: {library_url}")

    try:
        response = requests.get(library_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        all_divs = soup.select(".mb-4")

        if not all_divs:
            print("No links found. Website structure may have changed.")
            return

        scraped_data = []
        print("\n--- Found Introductory/Chapter Links ---")
        print("Beginning to scrape content from each link...\n")
        
        for div_tag in all_divs:
            link_tag = div_tag.find('a')
            if not link_tag:
                continue
            
            title = link_tag.get_text(strip=True)
            relative_url = link_tag.get('href')
            full_url = urljoin(base_url, relative_url)

            print(f"\nProcessing: {title}")
            content = scrape_page_content(full_url)

            page_entry = {
                "title": title,
                "url": full_url,
                "content": content,
                "subpages": []
            }

            # --- Scrape sub-links on this page ---
            try:
                sub_response = requests.get(full_url)
                sub_response.raise_for_status()
                sub_soup = BeautifulSoup(sub_response.text, 'html.parser')
                sub_links = sub_soup.select(".text-vb-link")

                for link in sub_links:
                    sub_title = link.get_text(strip=True)
                    sub_href = link.get("href")
                    if not sub_href:
                        continue

                    sub_url = urljoin(base_url, sub_href)
                    print(f"    ↳ Subpage: {sub_title}")
                    sub_content = scrape_page_content(sub_url)

                    page_entry["subpages"].append({
                        "title": sub_title,
                        "url": sub_url,
                        "content": sub_content
                    })
                    time.sleep(1)

            except Exception as e:
                print(f"    [Error] Failed to extract sub-links for {title}: {e}")

            scraped_data.append(page_entry)
            time.sleep(1)

        # Save all scraped data to JSON
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, ensure_ascii=False, indent=4)
        
        print(f"\n✅ Scraping complete. Data for {len(scraped_data)} pages saved to '{output_filename}'")

    except requests.exceptions.RequestException as e:
        print(f"[Error] Failed to fetch index page: {e}")
    except Exception as e:
        print(f"[Error] Unexpected error: {e}")

if __name__ == "__main__":
    scrape_vedabase_bg_chapters()
