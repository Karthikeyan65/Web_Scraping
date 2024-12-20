from playwright.sync_api import sync_playwright

def run_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  
        
        page = browser.new_page()
        
        page.goto("https://example.com")
        
        page.screenshot(path="screenshot.png")
        print("Screenshot saved as screenshot.png")
        
        print("Page Title:", page.title())
        
        browser.close()

if __name__ == "__main__":
    run_playwright()
