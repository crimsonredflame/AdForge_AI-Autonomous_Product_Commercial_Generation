import os
import asyncio
import httpx
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# Disguise our scraper so Amazon doesn't immediately block us
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

async def download_image(client, url, idx, out_dir="app/product_images"):
    """Downloads an image asynchronously and saves it to a local folder."""
    os.makedirs(out_dir, exist_ok=True)
    try:
        response = await client.get(url, timeout=10.0)
        if response.status_code == 200:
            path = f"{out_dir}/img_{idx}.jpg"
            with open(path, "wb") as f:
                f.write(response.content)
            return path
    except Exception as e:
        print(f"Failed to download {url}: {e}")
    return None

async def scrape_product(url: str):
    """Navigates to Amazon, extracts product data, and triggers image downloads."""
    print(f"Scraping Amazon URL: {url}")
    
    # 1. Fire up a headless browser
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(user_agent=HEADERS["User-Agent"])
        page = await ctx.new_page()
        
        # Load page and wait for dynamic content
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000) 
        html = await page.content()
        await browser.close()

    # 2. Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    title_element = soup.find(id="productTitle")
    title = title_element.get_text(strip=True) if title_element else "Unknown Product"

    price = "Price not found"
    for sel in ["span.a-price-whole", "span#priceblock_ourprice"]:
        p_el = soup.select_one(sel)
        if p_el:
            price = p_el.get_text(strip=True)
            break

    bullets = [li.get_text(strip=True) for li in soup.select("#feature-bullets li span.a-list-item") if len(li.get_text(strip=True)) > 10]
    description = " ".join(bullets[:3]) if bullets else "No description available."

    # 3. Extract High-Res Images (Amazon hides these in JavaScript variables)
    img_urls = []
    scripts = soup.find_all("script", string=re.compile("colorImages|imageGalleryData"))
    for s in scripts:
        matches = re.findall(r'"hiRes"\s*:\s*"(https[^"]+)"', s.string or "")
        img_urls.extend(matches)
    
    if not img_urls:
        og = soup.find("meta", property="og:image")
        if og:
            img_urls.append(og["content"])

    # Deduplicate and keep only the top 4 images
    img_urls = list(dict.fromkeys(img_urls))[:4] 

    # 4. Download those 4 images concurrently 
    image_paths = []
    async with httpx.AsyncClient(headers=HEADERS) as client:
        tasks = [download_image(client, url, idx) for idx, url in enumerate(img_urls)]
        results = await asyncio.gather(*tasks)
        image_paths = [path for path in results if path is not None]

    print(f"Successfully scraped: {title[:30]}... | Saved {len(image_paths)} images.")
    
    # 5. Return the clean data dictionary
    return {
        "title": title,
        "price": price,
        "description": description,
        "image_paths": image_paths
    }