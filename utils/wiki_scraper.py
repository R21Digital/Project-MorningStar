try:
    import requests
except ImportError as exc:
    print("Error: the 'requests' package is required. Install it with 'pip install requests'.")
    raise SystemExit(1) from exc

try:
    from bs4 import BeautifulSoup
except ImportError as exc:
    print("Error: the 'bs4' package (BeautifulSoup) is required. Install it with 'pip install beautifulsoup4'.")
    raise SystemExit(1) from exc


class WikiScraper:
    BASE_URL = "https://swgr.org/wiki/"

    def __init__(self):
        pass

    def fetch_page(self, page_path):
        url = self.BASE_URL + page_path
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch {url}")
        return response.text

    def parse_tables(self, html):
        soup = BeautifulSoup(html, "html.parser")
        tables = soup.find_all("table", class_="wikitable")
        data = []
        for table in tables:
            headers = [th.get_text(strip=True) for th in table.find_all("th")]
            for row in table.find_all("tr")[1:]:
                cells = [td.get_text(strip=True) for td in row.find_all("td")]
                if len(cells) == len(headers):
                    entry = dict(zip(headers, cells))
                    data.append(entry)
        return data


# Quick test
if __name__ == "__main__":
    scraper = WikiScraper()
    html = scraper.fetch_page("patch_notes/")
    tables = scraper.parse_tables(html)
    print("Found rows:", len(tables))
    print(tables[:2])
