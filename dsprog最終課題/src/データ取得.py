import requests
import time

class WikiFetcher:
    def fetch_length(self, area_name):
        url = "https://ja.wikipedia.org/w/api.php"
        params = {"action": "query", "format": "json", "titles": area_name, "prop": "info"}
        try:
            time.sleep(1.0)
            res = requests.get(url, params=params).json()
            pages = res.get("query", {}).get("pages", {})
            for pid, info in pages.items():
                return info.get("length", 0) if pid != "-1" else 0
        except:
            return 0