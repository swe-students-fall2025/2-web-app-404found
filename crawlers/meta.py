import asyncio
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from bs4 import BeautifulSoup

import json
from bs4 import BeautifulSoup

async def fetch_job_detail(crawler, job_url):
    """Fetch job details directly from the embedded JSON-LD data."""
    run_cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        js_code=["await new Promise(r => setTimeout(r, 3000));"],
        wait_for_timeout=15000
    )
    result = await crawler.arun(job_url, config=run_cfg)
    soup = BeautifulSoup(result.html, "html.parser")

    # Find the JSON-LD script tag
    script_tag = soup.find("script", {"type": "application/ld+json"})
    if not script_tag:
        print(f"⚠️ No JSON-LD data found for {job_url}")
        return None

    data = json.loads(script_tag.string)

    # Store Data
    job_info = {
        "jobID": job_url.split("/")[-1],
        "title": data.get("title"),
        "datePosted": data.get("datePosted"),
        "location": [loc.get("name") for loc in data.get("jobLocation", [])],
        "description": data.get("description"),
        "qualifications": data.get("qualifications"),
        "employmentType": data.get("employmentType"),
        "url": data.get("url", job_url)
    }

    return job_info


async def main():
    browser_cfg = BrowserConfig(headless=True)
    job_list_cfg = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        js_code=[
            "window.scrollTo(0, document.body.scrollHeight);",
            "await new Promise(r => setTimeout(r, 3000));"
        ],
        wait_for="a[href*='/jobs/']",
        wait_for_timeout=20000
    )

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # 1. Crawl main job list
        result = await crawler.arun("https://www.metacareers.com/jobs?page=1", config=job_list_cfg)
        soup = BeautifulSoup(result.html, "html.parser")

        job_links = []
        for a in soup.find_all("a", href=True):
            if a["href"].startswith("/jobs/"):
                full_url = f"https://www.metacareers.com{a['href']}"
                if full_url not in job_links:
                    job_links.append(full_url)

        print(f"✅ Found {len(job_links)} job links.")

        # 2. For each job, get details
        job_data = []
        for i, link in enumerate(job_links, start=1):
            print(f"Fetching ({i}/{len(job_links)}): {link}")
            try:
                detail = await fetch_job_detail(crawler, link)
                job_data.append(detail)
            except Exception as e:
                print(f"❌ Failed {link}: {e}")

        # 3. Save all to JSON, later to MongoDB
        with open("./job_posts/meta_jobs_data.json", "w", encoding="utf-8") as f:
            json.dump(job_data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Saved {len(job_data)} jobs to meta_jobs_data.json")

if __name__ == "__main__":
    asyncio.run(main())
