from typing import Optional
from pydantic import BaseModel, HttpUrl
from typing import List
from crawl4ai import (
    AsyncWebCrawler,
    CrawlResult,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
    CacheMode,
)


class SingleScrapeRequest(BaseModel):
    url: HttpUrl


class BatchScrapeRequest(BaseModel):
    urls: List[HttpUrl]


class ScrapeResponse(BaseModel):
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None


class BatchScrapeResponse(BaseModel):
    success: bool
    results: List[dict] = []
    error: Optional[str] = None


async def scrape(url: HttpUrl) -> ScrapeResponse:

    try:
        async with AsyncWebCrawler() as crawler:
            result: CrawlResult = await crawler.arun(
                url=str(url),
                config=CrawlerRunConfig(
                    exclude_external_links=True,
                    markdown_generator=DefaultMarkdownGenerator(
                        content_filter=PruningContentFilter()
                    ),
                    exclude_social_media_links=True,
                    cache_mode=CacheMode.BYPASS,
                ),
            )
            if result.success:
                return ScrapeResponse(
                    success=True,
                    content=result.markdown_v2.fit_markdown,
                )
            else:
                return ScrapeResponse(success=False, error="Failed to scrape content")
    except Exception as e:
        return ScrapeResponse(success=False, error=f"Scraping failed: {str(e)}")


async def scrape_batch(urls: List[HttpUrl]) -> BatchScrapeResponse:

    try:
        results = []
        async with AsyncWebCrawler() as crawler:
            # Use arun_many for parallel crawling
            crawl_results = await crawler.arun_many(
                urls=[str(url) for url in urls],
                config=CrawlerRunConfig(
                    exclude_external_links=True,
                    markdown_generator=DefaultMarkdownGenerator(
                        content_filter=PruningContentFilter()
                    ),
                    exclude_social_media_links=True,
                    cache_mode=CacheMode.BYPASS,
                    stream=False,
                ),
            )

            # Process results
            for result in crawl_results:
                if result.success:
                    results.append(
                        {
                            "url": result.url,
                            "content": result.markdown_v2.fit_markdown,
                            "success": True,
                        }
                    )
                else:
                    results.append(
                        {
                            "url": result.url,
                            "success": False,
                            "error": result.error_message or "Failed to scrape content",
                        }
                    )

        return BatchScrapeResponse(success=True, results=results)

    except Exception as e:
        return BatchScrapeResponse(
            success=False, error=f"Batch scraping failed: {str(e)}"
        )
