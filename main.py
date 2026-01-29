import json
from playwright.sync_api import sync_playwright


ENTERTAINMENT_URL = "https://ekantipur.com/entertainment"
CARTOON_URL = "https://ekantipur.com/cartoon"
MAX_ARTICLES = 5

def scrape_entertainment(page):
    """
    Task 1: Entertainment News

    - Navigate to entertainment page.
    - Wait for `.listLayout .row`.
    - Use a standard Python loop to work with the first row only.
    - From that row:
        * Get category name from `.cat_name`
        * Extract top 5 `article.normal` articles
        * For each article, get Title (h2), Author (.author), and Image
          (handle lazy loading: data-src first, then src).
    """
    page.goto(ENTERTAINMENT_URL, wait_until="domcontentloaded")
    page.wait_for_selector(".listLayout .row", timeout=15000)

    rows = page.query_selector_all(".listLayout .row")
    if not rows:
        return {"category": None, "articles": []}

    # Work with the first row only
    found_category=None
    articles_data = []
    
    for row in rows:
        category_el = row.query_selector(".cat_name")
        category_text = category_el.inner_text().strip() if category_el else None
        if "मनोरञ्जन" not in category_text:
            continue

        found_category = category_text
        
    # Extract top 5 `article.normal` within the first row
        article_nodes = row.query_selector_all("article.normal")
        
        for article in article_nodes[:MAX_ARTICLES]:
          # Title from h2
          title_el = article.query_selector("h2")
          title = title_el.text_content().strip() if title_el else None

        # Author from .author
          author_el = article.query_selector(".author")
          author = author_el.text_content().strip() if author_el else None

        # Image: data-src first, then src
          img_el = article.query_selector("img")
          image = None
          if img_el:
            image = img_el.get_attribute("data-src") or img_el.get_attribute("src")

          articles_data.append(
            {
                "title": title,
                "author": author,
                "image": image,
            }
        )
        break

    return {
        "category": category_text,
        "articles": articles_data,
    }


def scrape_cartoon(page):
    """
    Task 2: Cartoon of the Day

    - Navigate to cartoon page.
    - Wait for `.catroon-wrap` (note the typo).
    - Extract image src (handle lazy loading with data-src then src) and alt (as title).
    - Extract author from nested element `.cartoon-author`.
    """
    page.goto(CARTOON_URL, wait_until="domcontentloaded")
    page.wait_for_selector(".catroon-wrap", timeout=15000)

    wrap = page.query_selector(".catroon-wrap")
    if not wrap:
        return {"title": None, "image": None, "author": None}

    img = wrap.query_selector("img")
    image = (img.get_attribute("data-src") or img.get_attribute("src")) if img else None
    title = img.get_attribute("alt") if img else None

    author_el = page.query_selector(".cartoon-author")
    author = author_el.text_content().strip() if author_el else None

    return {
        "title": title,
        "image": image,
        "author": author,
    }


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("Scraping entertainment news...")
        entertainment_data = scrape_entertainment(page)
        print("Scraping cartoon of the day...")
        cartoon_data = scrape_cartoon(page)
        print("Scraping complete!")

        browser.close()

    output = {
        "entertainment_news": entertainment_data,
        "cartoon_of_the_day": cartoon_data,
    }

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
