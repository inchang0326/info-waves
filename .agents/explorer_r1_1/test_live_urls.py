import sys
from playwright.sync_api import sync_playwright

def test_url(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        print(f"\n--- Testing URL: {url} ---")
        try:
            page.goto(url, wait_until="networkidle", timeout=15000)
            title = page.title()
            print(f"Page Title: {title}")
            
            # Check search inputs
            inputs = page.query_selector_all("input")
            print(f"Found {len(inputs)} inputs on page.")
            for i, inp in enumerate(inputs):
                val = inp.get_attribute("value")
                ph = inp.get_attribute("placeholder")
                inp_type = inp.get_attribute("type")
                print(f" Input {i+1}: type='{inp_type}', placeholder='{ph}', value='{val}'")

            # Check search modal / sheet / DOM content
            text_content = page.content()
            if "강남구" in text_content:
                print(" -> Query string '강남구' was found in rendered DOM content!")
            else:
                print(" -> Query string '강남구' was NOT found in rendered DOM content.")
        except Exception as e:
            print(f"Error testing {url}: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    candidates = [
        "https://xn--v69ak0xskm.com/?q=%EA%B0%95%EB%82%A8%EA%B5%AC",
        "https://xn--v69ak0xskm.com/?search=%EA%B0%95%EB%82%A8%EA%B5%AC",
        "https://xn--v69ak0xskm.com/?address=%EA%B0%95%EB%82%A8%EA%B5%AC",
        "https://xn--v69ak0xskm.com/?query=%EA%B0%95%EB%82%A8%EA%B5%AC",
        "https://xn--v69ak0xskm.com/?keyword=%EA%B0%95%EB%82%A8%EA%B5%AC",
    ]
    for candidate in candidates:
        test_url(candidate)
