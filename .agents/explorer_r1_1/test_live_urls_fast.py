import sys
import requests
import urllib.parse

def test_http(param_name, val):
    encoded = urllib.parse.quote(val)
    url = f"https://xn--v69ak0xskm.com/?{param_name}={encoded}"
    try:
        resp = requests.get(url, timeout=5)
        print(f"Testing URL: {url} -> Status: {resp.status_code}, Length: {len(resp.text)}", flush=True)
    except Exception as e:
        print(f"Error testing {url}: {e}", flush=True)

if __name__ == "__main__":
    for param in ["q", "search", "address", "query", "keyword"]:
        test_http(param, "강남구")
