import asyncio
import json
from typing import List, Dict
from playwright.async_api import async_playwright, Browser, TimeoutError as PlaywrightTimeoutError

# In your test.py, only this function needs to be updated.

async def get_yahoo_article_content(browser: Browser, url: str) -> Dict[str, str]:
    """
    Extracts the main article content from a given Yahoo Finance URL.
    This final version uses highly specific locators to avoid strict mode violations.
    """
    page = await browser.new_page()
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        # Handle consent dialog (this logic is good)
        try:
            consent_frame_locator = page.frame_locator('iframe[title="Consent Management Z Dialog"]')
            await consent_frame_locator.locator('button:has-text("Accept all")').click(timeout=7000)
        except Exception:
            pass # Ignore if not found

        # Wait for the main content area to ensure the page is ready
        await page.wait_for_selector("main", timeout=15000)
        
        # Click "Continue Reading" if it exists (this logic is good)
        try:
            continue_btn = page.locator("button:has-text('Continue Reading')")
            if await continue_btn.is_visible(timeout=5000):
                await continue_btn.click()
                await page.wait_for_load_state('networkidle', timeout=20000)
        except Exception:
            pass

        # --- FINAL FIX ---
        # 🎯 Use specific locators for title and time to get exactly one element.
        # The error log showed 'h1.cover-title' is the correct title.
        title_locator = page.locator("h1.cover-title")
        
        # We'll use a similarly specific locator for the timestamp.
        time_locator = page.locator("time.byline-attr-meta-time")

        # The fallback logic for the article body is working well, so we keep it.
        article_locator = page.locator('div.caas-body')
        try:
            await article_locator.first.wait_for(timeout=10000)
        except PlaywrightTimeoutError:
            # This fallback is a good robust feature.
            # print(f"Warning: Could not find 'div.caas-body' on {url}. Falling back to the main <article> tag.")
            article_locator = page.locator('article').first
            await article_locator.wait_for(timeout=5000)

        # Now we extract the text using our specific locators.
        title_text = await title_locator.inner_text()
        time_text = await time_locator.inner_text()
        full_text = await article_locator.inner_text()
        
        return {
            "title": title_text.strip(),
            "date": time_text.strip(),
            "content": full_text.strip()
        }
    except Exception as e:
        return {
            "url": url,
            "error": f"Error extracting content: {type(e).__name__}: {e}"
        }
    finally:
        await page.close()

async def scrape_news(ticker: str, num_url: int = 5) -> List[Dict[str, str]]:
    """
    为给定的股票代码从雅虎财经抓取新闻文章。
    """
    print(f"Starting to scrape Yahoo Finance news for {ticker}")
    news_page_url = f"https://finance.yahoo.com/quote/{ticker}/news/"
    
    unique_article_urls = []
    async with async_playwright() as p:
        # 优化4: 调试时使用 headless=False，完成时改回 True
        browser = await p.chromium.launch(headless=True) 
        page = await browser.new_page()
        
        try:
            # ... (这部分逻辑保持不变，它工作得很好) ...
            await page.goto(news_page_url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_selector('li.stream-item', timeout=20000)
            
            links_locators = await page.query_selector_all('li.stream-item a[href]')
            
            seen_urls = set()
            for link_loc in links_locators:
                href = await link_loc.get_attribute('href')
                if href:
                    if href.startswith('/'):
                        href = f"https://finance.yahoo.com{href}"
                    
                    if "/news/" in href and ".html" in href:
                        clean_url = href.split('?')[0]
                        if clean_url not in seen_urls:
                           seen_urls.add(clean_url)
                           unique_article_urls.append(clean_url)
        except Exception as e:
            print(f"Error while scraping article links: {e}")
        finally:
            await page.close()

        if not unique_article_urls:
            print("Could not find any unique article URLs.")
            await browser.close()
            return []

        print(f"Found {len(unique_article_urls)} unique article links. Fetching content for the first {num_url}...")
        
        urls_to_fetch = unique_article_urls[:num_url]
        tasks = [get_yahoo_article_content(browser, url) for url in urls_to_fetch]
        articles = await asyncio.gather(*tasks)
        
        await browser.close()
    
    print("--------  Finished scraping Yahoo Finance news --------")
    return articles

async def main():
    results = await scrape_news(ticker="APPL", num_url=3)
    print(json.dumps(results, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())