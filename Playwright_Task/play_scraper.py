from playwright.sync_api import sync_playwright
import time

def scrape_incidents(date, max_pages=19):
    base_url = "https://www.wrps.on.ca/Modules/NewsIncidents/Search.aspx"
    params = {
        "feedId": "73a5e2dc-45fb-425f-96b9-d575355f7d4d",
        "keyword": "",
        "date": date  
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  
        for page_number in range(1, max_pages + 1):
            page = browser.new_page()
            
            params["page"] = page_number  
            url = f"{base_url}?feedId={params['feedId']}&keyword={params['keyword']}&date={params['date']}&page={page_number}"

            print(f"Loading page {page_number}...")
            page.goto(url)

            page.wait_for_load_state("networkidle")
            time.sleep(1)  

            incident_items = page.locator(".newsItem_Content")  

            count = incident_items.count()
            if count > 0:
                print(f"Incidents on {date} - Page {page_number}:")
                for i in range(count):
                    span_text = incident_items.nth(i).locator("p").inner_text(timeout=2000)
                    
                    print(f"\nIncident {i+1}:")
                    print(f"Title: {span_text.strip()}")
            else:
                print(f"No incidents found on page {page_number} for {date}.")

            page.close()

        browser.close()

if __name__ == "__main__":
    target_date = "12/18/2024"  
    scrape_incidents(target_date)
